from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from services.chat_service import ChatService
from dependencies.auth_dependencies import get_db
from dto.response import SuccessResponse
from dto.chat import StartConversationRequest, PostMessageRequest

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/start", response_model=SuccessResponse)
def start_conversation(data: StartConversationRequest, db: Session = Depends(get_db)):
    print("Starting conversation for user_id:", data.user_id)
    service = ChatService(db)
    conversation_id = service.create_conversation(data.user_id)
    return SuccessResponse(message="Conversation started", data={"conversation_id": conversation_id}, errors=None)


@router.get("/conversation/{conversation_id}", response_model=SuccessResponse)
def get_conversation(conversation_id:UUID, db: Session = Depends(get_db)):
    service = ChatService(db)
    messages = service.get_conversation(conversation_id)
    print(f"Fetched {len(messages)} messages for conversation_id: {conversation_id}")
    return SuccessResponse(
        message="Conversation fetched",
        data=[
            {"sender": m.sender.value, "text": m.message_text, "timestamp": m.created_at.isoformat()}
            for m in messages
        ],
        errors=None
    )


@router.post("/message", response_model=SuccessResponse)
def post_message( data:PostMessageRequest, db: Session = Depends(get_db)):
    service = ChatService(db)
    message = service.add_message(data.conversation_id, data.sender, data.text)
    return SuccessResponse(
        message="Message added",
        data={
            "sender": message.sender.value,
            "text": message.message_text,
            "timestamp": message.created_at.isoformat()
        },
        errors=None
    )
