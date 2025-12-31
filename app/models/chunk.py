from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"))
    document = relationship("Document", back_populates="chunks")
    
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    
    # 1536 is standard for OpenAI text-embedding-3-small, but we should probably configure it.
    # However, postgres vector definition requires a dimension.
    # We will assume 1536 for now or make it generic. 
    # For now, let's stick to 1536 (OpenAI standard).
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))
    
    # Metadata for filtering? Usually doc_id is enough.
