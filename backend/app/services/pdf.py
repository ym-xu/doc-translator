import fitz
from typing import List, Tuple, Dict
import json
from ..config import settings
import os

class PDFService:
    # 使用本地字体文件
    FONT_PATH = os.path.join(os.path.dirname(__file__), "../fonts/chinese")
    
    @staticmethod
    def init_fonts():
        """初始化字体"""
        os.makedirs(PDFService.FONT_PATH, exist_ok=True)
        font_path = os.path.join(PDFService.FONT_PATH, "NotoSansSC-Regular.otf")
        
        if not os.path.exists(font_path):
            import requests
            url = "https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/NotoSansSC-Regular.otf"
            response = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        
        return font_path

    @staticmethod
    def rgb_to_color(color: int) -> List[float]:
        """将整数RGB值转换为fitz可用的颜色格式 [r, g, b]"""
        blue = color & 255
        green = (color >> 8) & 255
        red = (color >> 16) & 255
        return [red / 255.0, green / 255.0, blue / 255.0]

    @staticmethod
    async def extract_text(file_path: str) -> List[Tuple[int, Dict]]:
        """从PDF文件中提取文本，返回更详细的文本信息"""
        try:
            doc = fitz.open(file_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_dict = page.get_text("dict", sort=True)
                
                for block in text_dict["blocks"]:
                    if block["type"] == 0:  # 文本块
                        block_text = ""
                        font_info = []
                        sizes = []
                        colors = []
                        
                        for line in block["lines"]:
                            for span in line["spans"]:
                                block_text += span["text"] + " "
                                font_info.append(span.get("font", ""))
                                sizes.append(span["size"])
                                colors.append(span["color"])
                        
                        block_text = block_text.strip()
                        if not block_text:
                            continue
                        
                        block_info = {
                            "text": block_text,
                            "rect": list(block["bbox"]),
                            "size": max(set(sizes), key=sizes.count) if sizes else 12,
                            "color": colors[0] if colors else 0,
                            "original_font": font_info[0] if font_info else "Helvetica"
                        }
                        text_blocks.append((page_num + 1, block_info))
            
            doc.close()
            return text_blocks
        except Exception as e:
            raise Exception(f"PDF文本提取失败: {str(e)}")

    @staticmethod
    async def create_translated_pdf(
        original_path: str,
        translated_blocks: List[Tuple[int, Dict]],
        output_path: str
    ):
        """创建翻译后的PDF文件，保持原有格式"""
        try:
            doc = fitz.open(original_path)
            
            # 删除原文本
            for page in doc:
                text_dict = page.get_text("dict")
                for block in text_dict["blocks"]:
                    if block["type"] == 0:
                        rect = fitz.Rect(block["bbox"])
                        page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions()
                page.clean_contents()
            
            # 写入翻译后的文本
            for page_num, block_info in translated_blocks:
                page = doc[page_num - 1]
                rect = fitz.Rect(block_info["rect"])
                text = block_info["text"]
                
                if not text or not text.strip():
                    continue
                    
                try:
                    # 使用基础字体
                    font_size = block_info["size"]
                    rect_height = rect.height
                    rect_width = rect.width
                    is_vertical = rect_height / rect_width > 10
                    
                    # 使用内置中文字体
                    font_name = "china-s"  # PyMuPDF内置中文字体
                    
                    if is_vertical:
                        # 垂直文本
                        page.insert_text(
                            point=(rect.x1, rect.y0),
                            text=text,
                            fontname=font_name,
                            fontsize=font_size,
                            color=(0, 0, 0),
                            rotate=90
                        )
                    else:
                        # 水平文本，自动调整大小
                        while True:
                            try:
                                rc = page.insert_textbox(
                                    rect,
                                    text,
                                    fontname=font_name,
                                    fontsize=font_size,
                                    color=(0, 0, 0),
                                    align=fitz.TEXT_ALIGN_LEFT
                                )
                                if rc >= 0:
                                    break
                                font_size *= 0.95
                                if font_size < 4:
                                    print(f"文本过长无法适配: {text[:50]}...")
                                    break
                            except Exception as e:
                                print(f"写入失败，尝试减小字体: {str(e)}")
                                font_size *= 0.95
                                if font_size < 4:
                                    break
                                
                except Exception as e:
                    print(f"处理文本块失败: {str(e)}, 文本: {text[:50]}...")
                    continue
            
            # 保存文件
            doc.save(
                output_path,
                clean=True,
                garbage=4,
                deflate=True,
                pretty=False
            )
            doc.close()
            
        except Exception as e:
            raise Exception(f"创建翻译PDF失败: {str(e)}")