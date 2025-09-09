from chromadb.api.models.Collection import Collection
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from dto.document import DocumentRequest
from dto.task import TaskStartRequest, TaskStartResponse, TaskStopRequest,TaskStopMessageResponse
from models.task_logs import TaskLogs
from models.tasks import Tasks
from models.projects import Projects
from models.users import Users
from models.task_assignees import TasksAssignees
from uuid import UUID
from datetime import datetime
from services.document_service import DocumentService


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_assigned_tasks(self, user_id: int):
        try:
            # Join tasks assigned to the ace_user_id, include project and supervisor
            rows = (
                self.db.query(
                    Tasks.ace_task_id.label("task_id"),
                    Projects.project_name.label("project_name"),
                    Tasks.task_title.label("task_name"),
                    Users.email.label("supervisor_name"),
                    Tasks.status.label("status")
                )
                .join(TasksAssignees, TasksAssignees.ace_task_id == Tasks.ace_task_id)
                .join(Projects, Projects.ace_project_id == Tasks.ace_project_id)
                .outerjoin(Users, Users.ace_user_id == Projects.supervisor_id)
                .filter(TasksAssignees.ace_user_id == user_id)
                .all()
            )

            return [
                {
                    "task_id": r.task_id,
                    "project_name": r.project_name,
                    "task_name": r.task_name,
                    "supervisor_name": r.supervisor_name,
                    "status": r.status,
                }
                for r in rows
            ]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
    
    def start_task(self, req: TaskStartRequest) -> TaskStartResponse:
        now = datetime.utcnow()


        existing_log = (
            self.db.query(TaskLogs)
            .filter(
                TaskLogs.ace_task_id == req.ace_task_id,
                TaskLogs.user_id == req.user_id,
                TaskLogs.end_time.is_(None),
            )
            .first()
        )

        if existing_log:
            log = existing_log
        else:
            log = TaskLogs(
                ace_task_id=req.ace_task_id,
                user_id=req.user_id,
                start_time=now,
                status=None,
                duration=None,
                comment=None,
                end_time=None
            )
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)

        return TaskStartResponse(
            log_id=log.log_id,
            ace_task_id=log.ace_task_id,
            user_id=log.user_id,
            status=log.status,
            duration=log.duration,
            start_time=log.start_time,
            end_time=log.end_time,
            comment=log.comment
        )

    async def stop_task(self, req: TaskStopRequest,col:Collection) -> TaskStopMessageResponse:
        
        log = self.db.query(TaskLogs).filter(TaskLogs.log_id == req.log_id).first()

        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

        now = datetime.utcnow()
        log.status = req.status
        log.comment = req.comment
        log.duration = req.duration
        log.end_time = now

        task = self.db.query(Tasks).filter(Tasks.ace_task_id == log.ace_task_id).first()
        if task:
            task.status = req.status  

        self.db.commit()
        self.db.refresh(log)

        task_name = task.task_title 
        project = self.db.query(Projects).filter(Projects.ace_project_id == task.ace_project_id).first()
        project_name = project.project_name 
        comment = f"{project_name} - {task_name}: {log.comment}"
        doc_request = {
            "id": [str(log.log_id)],
            "document": [comment],  # example: send the log comment
            "metadata": [{
                "status": log.status,
                "duration": log.duration,
                "start_time":str(log.start_time),
                "end_time": str(log.end_time)
            }]
        }
        request = DocumentRequest(**doc_request)
        try:
            response = await DocumentService(col).add_documents(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        
        return TaskStopMessageResponse(message="Task stopped successfully")