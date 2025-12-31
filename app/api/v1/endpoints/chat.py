from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.services import rag
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    top_k: int = 3

class ChatResponse(BaseModel):
    answer: str
    citations: list[dict]

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    # TODO: Verify user has access to docs? 
    # Current RAG implementation searches ALL chunks.
    # We must filter by user_id in the search!
    # Updating rag.py search function required for Multi-tenancy.
    
    result = await rag.generate_rag_response(session, request.query, current_user.id, request.top_k)
    return result

@router.get("/stream")
async def chat_stream(
    query: str,
    top_k: int = 3,
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    from fastapi.responses import StreamingResponse
    import json
    
    # Needs a generator function from RAG service
    # We'll update rag.py to support streaming generator.
    
    # For now, simplistic wrapper around generator
    async def event_generator():
        # First emit chunks used
        chunks = await rag.search_similar_chunks(session, query, current_user.id, top_k)
        citations = [{"doc_id": c.document_id, "text": c.text[:200]} for c in chunks]
        
        # Emit citations event
        yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
        
        # Then generate answer stream
        context_text = "\n\n".join([f"Snippet {i+1}: {chunk.text}" for i, chunk in enumerate(chunks)])
        prompt = f"Context:\n{context_text}\n\nQuestion:\n{query}\n\nAnswer:"
        
        from app.services.llm.factory import get_llm_provider
        llm = get_llm_provider()
        
        async for token in llm.generate_stream(prompt):
             yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"
             
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
