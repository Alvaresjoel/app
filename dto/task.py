from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# ---- START TASK ----
class TaskStartRequest(BaseModel):
    user_id: UUID
    ace_task_id: int

class TaskStartResponse(BaseModel):
    log_id: UUID 
    ace_task_id: int
    user_id: UUID
    status: Optional[str] = None
    duration: Optional[float] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    comment: Optional[str] = None

# ---- STOP TASK ----
class TaskStopRequest(BaseModel):
    log_id: UUID 
    status: str
    comment: Optional[str] = None
    duration: float

class TaskStopMessageResponse(BaseModel):
    message: str
