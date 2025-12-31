from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base

class DocStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    file_path: Mapped[str] = mapped_column(String)
    file_type: Mapped[str] = mapped_column(String, default="text") # txt, pdf, md
    
    status: Mapped[DocStatus] = mapped_column(SAEnum(DocStatus), default=DocStatus.UPLOADED)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
