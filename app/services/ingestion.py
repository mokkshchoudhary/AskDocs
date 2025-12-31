import asyncio
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.db.session import AsyncSessionLocal
from app.models.document import Document, DocStatus
from app.models.chunk import DocumentChunk
from app.services.embeddings.factory import get_embeddings_provider
from app.core import logging
from app.core.config import settings
from app.workers.celery_app import celery_app

logger = logging.logger

async def trigger_ingestion(doc_id: int, session: AsyncSession):
    """
    Trigger the background ingestion task.
    """
    from app.workers.tasks import process_document_task
    # Use delay to send to Celery
    process_document_task.delay(doc_id)

async def ingest_document(doc_id: int):
    """
    Core ingestion logic:
    1. Fetch doc
    2. Extract text
    3. Chunk
    4. Embed
    5. Save Chunks
    6. Update Status
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalars().first()
        if not doc:
            logger.error(f"Document {doc_id} not found in worker")
            return

        try:
            # Update status to PROCESSING
            doc.status = DocStatus.PROCESSING
            await session.commit()

            # 1. Extract Text
            text_content = ""
            file_path = doc.file_path
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at {file_path}")

            if doc.file_type == "pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            else:
                # Text or MD
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()

            if not text_content.strip():
                raise ValueError("No text content extracted")

            # 2. Chunking
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = splitter.split_text(text_content)
            logger.info(f"Document {doc_id}: Generated {len(chunks)} chunks.")

            # 3. Embeddings
            provider = get_embeddings_provider()
            # Batch embedding
            vectors = await provider.embed_documents(chunks)

            # 4. Save Chunks
            # Delete old chunks if any (re-ingestion case, though we usually just append or fail)
            # await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id)) # Not needed for fresh upload

            for i, (chunk_text, vector) in enumerate(zip(chunks, vectors)):
                db_chunk = DocumentChunk(
                    document_id=doc_id,
                    chunk_index=i,
                    text=chunk_text,
                    embedding=vector
                )
                session.add(db_chunk)

            # 5. Update Status
            doc.status = DocStatus.READY
            doc.error_message = None
            doc.updated_at = datetime.utcnow()
            await session.commit()
            logger.info(f"Document {doc_id} ingestion complete.")

        except Exception as e:
            logger.error(f"Ingestion failed for doc {doc_id}: {e}")
            await session.rollback() # Rollback chunks
            # Start new transaction for status update
            async with AsyncSessionLocal() as sess2:
                res2 = await sess2.execute(select(Document).where(Document.id == doc_id))
                doc2 = res2.scalars().first()
                if doc2:
                    doc2.status = DocStatus.FAILED
                    doc2.error_message = str(e)
                    await sess2.commit()
