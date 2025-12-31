import shutil
import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document, DocStatus
from app.schemas.document import DocumentOut
from app.services import ingestion

router = APIRouter()

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    # Validate file type
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".txt", ".md", ".pdf"]:
        raise HTTPException(400, "Only .txt, .md, .pdf files are supported")
    
    # Save file
    file_location = os.path.join(settings.UPLOAD_DIR, f"{filename}") # Should use UUID to avoid collision
    # Better: use UUID for storage
    import uuid
    storage_name = f"{uuid.uuid4()}{ext}"
    storage_path = os.path.join(settings.UPLOAD_DIR, storage_name)
    
    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc = Document(
        title=filename,
        file_path=storage_path,
        file_type=ext.replace(".", ""),
        status=DocStatus.UPLOADED,
        owner_id=current_user.id
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    
    # Trigger ingestion
    await ingestion.trigger_ingestion(doc.id, session)
    
    return doc

@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    result = await session.execute(
        select(Document).where(Document.owner_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(
        select(Document).where(Document.id == doc_id, Document.owner_id == current_user.id)
    )
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(
        select(Document).where(Document.id == doc_id, Document.owner_id == current_user.id)
    )
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if processing? Usually allow delete anyway.
    # Delete file? Yes.
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass # Log error
        
    await session.delete(doc)
    await session.commit()
    return {"status": "deleted"}
