from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.services.embeddings.factory import get_embeddings_provider
from app.services.llm.factory import get_llm_provider
from app.models.chunk import DocumentChunk
from app.core import logging

logger = logging.logger

async def search_similar_chunks(session: AsyncSession, query: str, owner_id: int, top_k: int = 5):
    """
    Embed query and search for similar chunks using pgvector, filtered by owner.
    """
    provider = get_embeddings_provider()
    query_vector = await provider.embed_text(query)
    
    # PGVector search
    # We join DocumentChunk with Document to filter by owner_id
    from app.models.document import Document
    
    stmt = select(DocumentChunk).join(Document)\
        .where(Document.owner_id == owner_id)\
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))\
        .limit(top_k)
    
    result = await session.execute(stmt)
    chunks = result.scalars().all()
    return chunks

async def generate_rag_response(session: AsyncSession, query: str, owner_id: int, top_k: int = 3):
    """
    Full RAG flow:
    1. Retrieve chunks
    2. Construct prompt
    3. Generate answer
    """
    chunks = await search_similar_chunks(session, query, owner_id, top_k)
    
    context_text = "\n\n".join([f"Snippet {i+1}: {chunk.text}" for i, chunk in enumerate(chunks)])
    
    prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.
If the answer is not in the context, say you don't know.

Context:
{context_text}

Question:
{query}

Answer:"""

    llm = get_llm_provider()
    answer = await llm.generate_response(prompt)
    
    citations = [{"doc_id": c.document_id, "text": c.text[:200]} for c in chunks]
    
    return {
        "answer": answer,
        "citations": citations
    }
