from sqlalchemy import Column, String, DateTime, Uuid, Integer
from uuid import uuid4
from connection.database import Base
from datetime import datetime as dt

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Uuid, primary_key=True, default=uuid4, nullable=False)
    ace_user_id = Column(Integer, nullable=False, unique=True)
    guid = Column(String(250))
    email = Column(String(200), unique=True, nullable=False)
    role = Column(String(150))
