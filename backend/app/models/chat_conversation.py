from sqlalchemy import Column, DateTime, Uuid
from datetime import datetime
from connection.database import Base
import uuid


class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)