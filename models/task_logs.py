from sqlalchemy import Column, String,Text, ForeignKey, Uuid, Float, Integer, DateTime
from uuid import uuid4
from connection.database import Base

class TaskLogs(Base):
    __tablename__ = "task_logs"

    log_id = Column(Uuid, primary_key=True, default=uuid4, nullable=False)
    ace_task_id = Column(Integer, ForeignKey("tasks.ace_task_id"))
    user_id = Column(Uuid, ForeignKey("users.user_id"))
    duration = Column(Float)                 
    comment = Column(Text)     
    status = Column(String(50)) 
    start_time = Column(DateTime)
    end_time = Column(DateTime)

