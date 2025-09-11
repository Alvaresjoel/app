from sqlalchemy import Column, ForeignKey, Text, DateTime, Enum, Uuid
from datetime import datetime
from connection.database import Base
import enum
import uuid


class SenderEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Uuid, ForeignKey("chat_conversations.id"), nullable=False)
    sender = Column(Enum(SenderEnum), nullable=False)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)