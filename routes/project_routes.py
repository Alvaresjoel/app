from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from dependencies.get_db import get_db
from services.project_service import ProjectService

router = APIRouter(
    prefix="/projects", 
    tags=["Projects"]
)

@router.post("/fetch-projects")
def fetch_projects(guid: str, db: Session = Depends(get_db)):
    project_service = ProjectService(db)
    return project_service.fetch_and_store_projects(guid)
