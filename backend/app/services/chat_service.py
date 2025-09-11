from sqlalchemy.orm import Session
from models.chat_conversation import ChatConversation
from models.chat_messages import ChatMessage
from uuid import UUID

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation(self, conversation_id: UUID):
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        return messages

    def create_conversation(self, user_id: UUID) -> UUID:
        fetched_conversation = (
            self.db.query(ChatConversation)
            .filter(ChatConversation.user_id == user_id)
            .first()
        )

        if fetched_conversation:
            return fetched_conversation.id

        conversation = ChatConversation(user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation.id

    def add_message(self, conversation_id: UUID, sender: str, text: str):
        message = ChatMessage(
            conversation_id=conversation_id,
            sender=sender,
            message_text=text
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
