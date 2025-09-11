from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Uuid
from uuid import uuid4
from connection.database import Base
from datetime import datetime as dt

class Projects(Base):
    __tablename__ = "projects"
    
    project_id = Column(Uuid, primary_key=True, default=uuid4, nullable=False)
    ace_project_id = Column(Integer, nullable=False, unique=True)
    project_name = Column(String(100), nullable=False)
    description = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    supervisor_id = Column(Integer, ForeignKey("users.ace_user_id"), nullable=True)
