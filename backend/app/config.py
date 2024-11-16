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
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    CLOUDFLARE_ACCOUNT_ID: str
    CLOUDFLARE_ACCESS_KEY_ID: str
    CLOUDFLARE_ACCESS_KEY_SECRET: str
    R2_BUCKET_NAME: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()