from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Uuid
from uuid import uuid4
from connection.database import Base
from datetime import datetime as dt

class Tasks(Base):
    __tablename__ = "tasks"
    
    task_id = Column(Uuid, primary_key=True, default=uuid4)
    ace_task_id = Column(Integer, nullable=False, unique=True)
    task_title = Column(String(100), nullable=False)
    description = Column(String(255))
    status = Column(String(50), nullable=True, default="In progress")
    ace_project_id = Column(Integer, ForeignKey("projects.ace_project_id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
