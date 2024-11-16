import boto3
from botocore.config import Config
from ..config import settings
import os

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.CLOUDFLARE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_ACCESS_KEY_SECRET,
            config=Config(signature_version='v4'),
        )
        self.bucket = settings.R2_BUCKET_NAME

    async def upload_file(self, file_path: str, object_name: str) -> str:
        """Upload file to R2 storage"""
        try:
            self.s3.upload_file(file_path, self.bucket, object_name)
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=3600 * 24
            )
            print(f"Generated presigned URL: {url}")
            return url
        except Exception as e:
            raise Exception(f"File upload failed: {str(e)}")

    async def download_file(self, object_name: str, file_path: str):
        """Download file from R2 storage"""
        try:
            self.s3.download_file(self.bucket, object_name, file_path)
        except Exception as e:
            raise Exception(f"File download failed: {str(e)}")