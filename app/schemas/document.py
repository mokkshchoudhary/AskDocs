from datetime import datetime
from pydantic import BaseModel
from app.models.document import DocStatus

class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    pass

class DocumentOut(DocumentBase):
    id: int
    file_path: str
    file_type: str
    status: DocStatus
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
