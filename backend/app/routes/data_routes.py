from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dto.task import RolloverRequest
from dependencies.get_db import get_db
from services.data_service import DataService
from dto.response import ErrorCode, ErrorResponse, SuccessResponse

router = APIRouter(prefix="/data", tags=["Data"])

@router.post("/save")
def save_all_data(guid: str, db: Session = Depends(get_db)):
    service = DataService(db)
    try:
        users_data = service.fetch_users(guid)
        projects_data = service.fetch_projects(guid)
        tasks_data = service.fetch_tasks(guid)
        assignees_inserted = service.save_task_assignees(guid)
        
        # ! CALLED ONLY ONCE PER WEEK(START OF THE WEEK) !!!!!!!!!!!!!!!!!!!!
        workitems_created = service.create_workitems(guid)
        return SuccessResponse (
            message="Users, Projects, Tasks, Assignees & WorkItems saved successfully",
            data={
                "users_count": len(users_data),
                "projects_count": len(projects_data),
                "tasks_count": len(tasks_data),
                "assignees_inserted": assignees_inserted,
                "workitems_created": workitems_created
            },
            error=None
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ! CALLED ONLY ONCE PER WEEK(END OF THE WEEK) !!!!!!!!!!!!!!!!!!!!
@router.post("/rollover", response_model=SuccessResponse | ErrorResponse)
def rollover_workitems_route(req: RolloverRequest, db: Session = Depends(get_db)):
    service = DataService(db)
    try:
        result = service.rollover_workitems(guid=req.guid, custom_comment=req.comment)
        # result is a dict: {"message": "...", "created": ...}
        return SuccessResponse(
            message=result.get("message", "Rollover completed"),
            data={"created": result.get("created", 0)}
        )

    except Exception as e:
        return ErrorResponse(
            message="Failed to rollover work items",
            error=str(e),
            error_code=ErrorCode.SERVICE_UNAVAILABLE
        )
