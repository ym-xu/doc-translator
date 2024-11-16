from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranslationJob(BaseModel):
    id: str
    file_name: str
    source_language: str
    target_language: str
    status: JobStatus
    progress: float = 0
    error: Optional[str] = None
    result_url: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class TranslationRequest(BaseModel):
    target_language: str