import asyncio
from app.workers.celery_app import celery_app
from app.services.ingestion import ingest_document
from app.core.logging import logger

@celery_app.task(acks_late=True)
def process_document_task(doc_id: int):
    logger.info(f"Starting processing for doc_id={doc_id}")
    try:
        asyncio.run(ingest_document(doc_id))
    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Could retry here
