from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import AssistantRequest
from app.services import assistant_service
from app.utils.response import ApiError, success

router = APIRouter(prefix="/assistant", tags=["assistant"])

MAX_MESSAGE_LENGTH = 1000


@router.post("/chat")
def chat(body: AssistantRequest, db: Session = Depends(get_db)):
    message = body.message.strip()
    if not message:
        raise ApiError(422, "EMPTY_MESSAGE", "Message must not be empty")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ApiError(422, "MESSAGE_TOO_LONG", f"Message must be at most {MAX_MESSAGE_LENGTH} characters")
    result = assistant_service.chat(db, message, body.conversation_id, body.project_id)
    return success(result.model_dump(mode="json"))


@router.get("/suggestions")
def suggestions():
    return success(assistant_service.SUGGESTIONS)
