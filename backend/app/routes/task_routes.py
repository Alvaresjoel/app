from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dto.response import ErrorCode, SuccessResponse, ErrorResponse

from dependencies.chromadb_dependency import get_chroma_collection
from chromadb.api.models.Collection import Collection

from dto.task import TaskStartRequest, TaskStartResponse, TaskStopRequest,TaskDurationResponse,TaskPauseRequest, TaskStopMessageResponse, TaskPauseMessageResponse

from services.task_service import TaskService
from dependencies.get_db import get_db
from uuid import UUID

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


@router.post("/stop", response_model=SuccessResponse | ErrorResponse)
def stop_task(request: TaskStopRequest, db: Session = Depends(get_db),col:Collection = Depends(get_chroma_collection)):
    service = TaskService(db)
    try:
        # Step 1: Stop the task first
        stop_response = service.stop_task(request,col)

        # Step 2: Call add_time_item automatically after stopping
        try:
            updated_count = service.add_time_item(
                guid=request.guid,        # Pass guid from request
                seconds=request.duration, # Time worked in seconds
                taskid=request.taskid     # Task ID for work item
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            return ErrorResponse(
                message="Error updating work item hours",
                error=str(e),
                error_code=ErrorCode.SERVICE_UNAVAILABLE
            )

        # Step 3: Return combined response
        return SuccessResponse(
            message="Task stopped and hours updated successfully",
            data={
                "stop_response": stop_response,
                "updated_count": updated_count
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        return ErrorResponse(
            message="Error stopping task",
            error=str(e),
            error_code=ErrorCode.SERVICE_UNAVAILABLE
        )

@router.post("/pause", response_model=TaskPauseMessageResponse)
def pause_task(request: TaskPauseRequest, db: Session = Depends(get_db)):
    return TaskService(db).pause_task(request)

@router.get("/duration/{log_id}", response_model=TaskDurationResponse)
def get_duration(log_id: UUID, db: Session = Depends(get_db)):
    return TaskService(db).get_duration_by_log_id(log_id)

@router.get("/latest-log/")
def get_latest_log(user_id, task_id, db: Session = Depends(get_db)):
    return TaskService(db).get_latest_log(task_id, user_id)

