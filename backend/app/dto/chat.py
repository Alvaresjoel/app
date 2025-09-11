from pydantic import BaseModel
from uuid import UUID

class StartConversationRequest(BaseModel):
    user_id: UUID

class GetConversationRequest(BaseModel):
    conversation_id: UUID

class PostMessageRequest(BaseModel):
    conversation_id: UUID
    sender: str
    text: str