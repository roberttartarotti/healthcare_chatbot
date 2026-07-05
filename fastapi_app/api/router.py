"""Main API router."""

from fastapi import APIRouter

from fastapi_app.api.endpoints import chat

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chat"])
