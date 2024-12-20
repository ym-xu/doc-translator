from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .models import TranslationJob, JobStatus, TranslationRequest
from .services.pdf import PDFService
from .services.translator import TranslatorService
from .services.storage import StorageService
import os
import uuid
import aiofiles
from typing import Dict
import uvicorn

# 删除代理设置，在 Render 上不需要
# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://doc-translator.pages.dev,https://api.cloudflare.com").split(",")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在应用启动时创建上传目录
upload_dir = os.path.join(os.path.dirname(__file__), "..", settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)

# 存储任务状态
jobs: Dict[str, TranslationJob] = {}

# 初始化服务
storage_service = StorageService()

async def process_translation(job_id: str, file_path: str, translated_path: str, target_language: str):
    """后台任务处理翻译"""
    try:
        if job_id not in jobs:
            print(f"Task {job_id} does not exist")
            return
            
        job = jobs[job_id]
        job.status = JobStatus.PROCESSING
        print(f"Starting to process task {job_id}")
        
        # 提取文本
        try:
            print(f"Starting to extract PDF text: {file_path}")
            text_blocks = await PDFService.extract_text(file_path)
            print(f"Successfully extracted text, total {len(text_blocks)} text blocks")
            
            # 打印前两个文本块示例
            if text_blocks:
                print("Text block examples:")
                for i, (page, block_info) in enumerate(text_blocks[:2]):
                    print(f"Page {page}: {block_info['text'][:100]}...")
            
        except Exception as e:
            print(f"PDF text extraction failed: {str(e)}")
            job.status = JobStatus.FAILED
            job.error = f"PDF text extraction failed: {str(e)}"
            return
            
        # 翻译文本
        try:
            print(f"Starting translation to {target_language}")
            async def update_progress(progress: float):
                job.progress = progress
                print(f"Translation progress: {progress:.2f}%")
            
            translated_blocks = await TranslatorService.translate_blocks(
                text_blocks,
                target_language,
                update_progress
            )
            print("Translation completed")
            
        except Exception as e:
            print(f"Translation failed: {str(e)}")
            job.status = JobStatus.FAILED
            job.error = f"Translation failed: {str(e)}"
            return
            
        # 创建新PDF
        try:
            print("Starting to generate translated PDF")
            output_path = f"{settings.UPLOAD_DIR}/translated_{job.file_name}"
            await PDFService.create_translated_pdf(file_path, translated_blocks, output_path)
            print(f"PDF generation completed: {output_path}")
            
            # 上传到R2存储
            print("Starting upload to R2 storage")
            result_url = await storage_service.upload_file(
                output_path,
                f"translated/{job_id}/{job.file_name}"
            )
            print(f"Upload completed, URL: {result_url}")
            
            # 更新任务状态
            job.status = JobStatus.COMPLETED
            job.result_url = result_url
            job.progress = 100
            print(f"Task {job_id} processing completed, result_url: {result_url}")
            
            # 清理临时文件
            os.remove(file_path)
            os.remove(output_path)
            print("Temporary files cleaned up")
            
        except Exception as e:
            print(f"PDF generation or upload failed: {str(e)}")
            job.status = JobStatus.FAILED
            job.error = f"PDF generation or upload failed: {str(e)}"
            try:
                os.remove(file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Task processing failed: {str(e)}")
        if job_id in jobs:
            jobs[job_id].status = JobStatus.FAILED
            jobs[job_id].error = str(e)
        try:
            os.remove(file_path)
        except:
            pass

@app.post(f"{settings.API_PREFIX}/translate")
async def create_translation(
    file: UploadFile = File(...),
    target_language: str = "zh",
    background_tasks: BackgroundTasks = None
):
    """创建翻译任务"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 创建上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 生成任务ID
    job_id = str(uuid.uuid4())
    file_path = f"{settings.UPLOAD_DIR}/{job_id}_{file.filename}"
    
    # 保存上传的文件
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # 创建任务
    job = TranslationJob(
        id=job_id,
        file_name=file.filename,
        source_language="auto",
        target_language=target_language,
        status=JobStatus.PENDING,
    )
    jobs[job_id] = job
    
    # 启动后台任务
    background_tasks.add_task(
        process_translation,
        job_id,
        file_path,
        f"{settings.UPLOAD_DIR}/translated_{file.filename}",
        target_language
    )
    
    return {
        "jobId": job_id,
        "status": job.status,
        "translatedPdfUrl": job.result_url
    }

@app.get(f"{settings.API_PREFIX}/jobs/{{job_id}}")
async def get_job_status(job_id: str):
    """获取任务状态"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="任务不存在")
    return jobs[job_id]

@app.get(f"{settings.API_PREFIX}/jobs/{{job_id}}/download")
async def download_result(job_id: str):
    """下载翻译结果"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    job = jobs[job_id]
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="翻译尚未完成")
    
    if not job.result_url:
        raise HTTPException(status_code=400, detail="翻译结果不可用")
    
    return {"url": job.result_url}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)