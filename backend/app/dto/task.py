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
    guid: str
    taskid: int
    userid: UUID
    status: str
    comment: Optional[str] = None
    duration: float

class TaskStopMessageResponse(BaseModel):
    message: str

class TimeItemRequest(BaseModel):
    guid: str
    ace_task_id: str
    day: str
    hours: float

class UpdateWorkItemHoursRequest(BaseModel):
    guid: str
    seconds: float
    taskid: int

class RolloverRequest(BaseModel):
    guid: str
    comment: str

class TaskPauseRequest(BaseModel):
    log_id: UUID
    duration: Optional[int] = None

class TaskPauseMessageResponse(BaseModel):
    message: str

class TaskDurationResponse(BaseModel):
    log_id: UUID
    duration: Optional[int]

