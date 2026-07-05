"""Chat endpoint.

A single POST /chat: send a message and get the assistant's reply. The same
``user_id`` should be reused across calls — it is the conversation thread, so the
assistant remembers context (and only shows the disclaimer on the first message).
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from healthcare_assistant_lib import send_message

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    user_id: str = Field(description="Stable per-user id; reused across the conversation.")
    message: str = Field(description="The user's message.")


class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""

    reply: str
    specialty: str
    blocked: bool


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Send a user message and return the assistant's reply.

    The reply is produced by the multi-agent graph (supervisor -> specialist).
    On the first message of a conversation it is prefixed with the mandatory
    disclaimer. ``specialty`` shows which specialist answered; ``blocked`` is True
    when the input guardrail refused (off-topic or possible emergency).
    """
    result = send_message(request.user_id, request.message)
    return ChatResponse(**result)
