from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.chromadb_dependency import get_chroma_collection
from chromadb.api.models.Collection import Collection

from dto.task import TaskStartRequest, TaskStartResponse, TaskStopRequest, TaskStopMessageResponse
from services.task_service import TaskService
from dependencies.get_db import get_db

router = APIRouter(
    prefix="/tasks", 
    tags=["tasks"]
)

@router.get("/{user_id}")
def fetch_tasks(user_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.fetch_assigned_tasks(user_id)

@router.post("/start", response_model=TaskStartResponse)
def start_task(request: TaskStartRequest, db: Session = Depends(get_db)):
    return TaskService(db).start_task(request)

@router.post("/stop", response_model=TaskStopMessageResponse)
async def stop_task(request: TaskStopRequest, db: Session = Depends(get_db),col : Collection = Depends(get_chroma_collection)):
    return await TaskService(db).stop_task(request,col)
