from fastapi import APIRouter
from app.api.v1.endpoints import auth, docs, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
