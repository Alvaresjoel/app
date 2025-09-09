from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies.get_db import get_db
from services.data_service import DataService
from dto.response import SuccessResponse

router = APIRouter(prefix="/data", tags=["Data"])

@router.post("/save")
def save_all_data(guid: str, db: Session = Depends(get_db)):
    service = DataService(db)
    try:
        users_data = service.fetch_users(guid)
        projects_data = service.fetch_projects(guid)
        tasks_data = service.fetch_tasks(guid)
        assignees_inserted = service.save_task_assignees(guid)
        return SuccessResponse (
            message="Users, Projects, Tasks & Assignees saved successfully",
            data={
                "users_count": len(users_data),
                "projects_count": len(projects_data),
                "tasks_count": len(tasks_data),
                "assignees_inserted": assignees_inserted
            },
            error=None
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
