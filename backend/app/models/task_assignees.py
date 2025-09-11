from sqlalchemy import Column, DateTime, ForeignKey, Integer, Uuid
from uuid import uuid4
from connection.database import Base
from datetime import datetime as dt

class TasksAssignees(Base):
    __tablename__ = "tasks_assignees"
    
    task_assignee_id = Column(Uuid, primary_key=True, default=uuid4, nullable=False)
    ace_task_id = Column(Integer, ForeignKey("tasks.ace_task_id"))
    assigned_at = Column(DateTime)
    ace_user_id = Column(Integer, ForeignKey("users.ace_user_id"))
    time_line_id = Column(Integer)
