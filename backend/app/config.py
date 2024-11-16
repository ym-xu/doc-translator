from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 确保在类定义前加载环境变量
load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doc Translator"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    UPLOAD_DIR: str = "uploads"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # 显式从环境变量加载
    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_ACCESS_KEY_ID: str
    CLOUDFLARE_ACCESS_KEY_SECRET: str
    R2_BUCKET_NAME: str
    # PDF_FONT_PATH: str = "fonts/SourceHanSerif-VF.ttf"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# 添加调试信息
print("=== Settings Debug ===")
print(f"OPENAI_API_KEY loaded: {'*' * len(settings.OPENAI_API_KEY)}")
print("===================")

print(settings)