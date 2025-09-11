from chromadb.api.models.Collection import Collection
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dto.task import TaskStartRequest, TaskStartResponse, TaskStopRequest,TaskStopMessageResponse, TimeItemRequest
from dto.response import SuccessResponse, ErrorResponse, ErrorCode

from dto.document import DocumentRequest


from models.task_logs import TaskLogs
from models.tasks import Tasks
from models.projects import Projects
from models.users import Users
from models.task_assignees import TasksAssignees
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os
import math
import requests

load_dotenv()
ACE_API_URL = os.getenv('ACE_API_URL')

from services.document_service import DocumentService


from uuid import UUID

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
                    Users.username.label("supervisor_name"),
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
        now = datetime.now()


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

        now = datetime.now()
        log.status = req.status
        log.comment = req.comment
        log.duration = req.duration
        log.end_time = now

        task = self.db.query(Tasks).filter(Tasks.ace_task_id == log.ace_task_id).first()
        if task:
            task.status = req.status  
        user = self.db.query(Users).filter(Users.user_id == req.userid).first()
        self.db.commit()
        self.db.refresh(log)
        task_name = task.task_title 
        project = self.db.query(Projects).filter(Projects.ace_project_id == task.ace_project_id).first()
        project_name = project.project_name 
        comment = f"{project_name} - {task_name}: {log.comment}"
        doc_request = {
            "id": [str(uuid.uuid4())],
            "document": [comment],  # example: send the log comment
            "metadata": [{
                "log_id":str(log.log_id),
                "ace_task_id":log.ace_task_id,
                "user_id":str(log.user_id),
                "status": log.status,
                "duration": math.ceil(log.duration/900)*0.25 if log.duration else 0,
                "start_time":str(log.start_time.timestamp()),
                "end_time": str(log.end_time),
                "username": user.username
            }]
        }
        request = DocumentRequest(**doc_request)
        try:
            response = await DocumentService(col).add_documents(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return TaskStopMessageResponse(message="Task stopped successfully")
    
    def pause_task(self, req: TaskStopRequest) -> TaskStopMessageResponse:
        log = self.db.query(TaskLogs).filter(TaskLogs.log_id == req.log_id).first()

        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

        log.duration = req.duration

        self.db.commit()
        self.db.refresh(log)
        return TaskStopMessageResponse(message="Task stopped successfully")
    

    @staticmethod
    def seconds_to_custom_hours(seconds: int) -> float:
        # 1 block = 15 mins = 900 seconds
        blocks = math.ceil(seconds / 900)  # Round up to nearest block
        return blocks * 0.25  # Each block = 0.25 hours


    def add_time_item(self, guid: str, taskid: int, seconds: int) -> int:
        """
        Take time in seconds → convert to hours (rounded to 15 min blocks) → store in ACE API.
        """
        if not ACE_API_URL:
            raise Exception("ACE_API_URL is not configured in environment")

        # Convert seconds → hours
        final_hours = TaskService.seconds_to_custom_hours(seconds)

        # Ensure valid hours 0–24
        if final_hours <= 0 or final_hours > 24:
            raise ValueError(f"Hours must be between 0 and 24 after conversion. Got: {final_hours}")

        # Determine day of week: Sunday=1, Monday=2, ..., Saturday=7
        today = datetime.now()
        day_of_week = ((today.weekday() + 1) % 7) + 1

        # Fetch task
        task = self.db.query(TasksAssignees).filter(TasksAssignees.ace_task_id == taskid).first()
        if not task:
            raise ValueError(f"Task with ace_task_id {taskid} not found")
        if not task.time_line_id:
            raise ValueError(f"Task with ace_task_id {taskid} has no time_line_id set")

        # Prepare payload for ACE API
        payload = {
            "fct": "savetimeitemhours",
            "guid": guid,
            "timesheetlineid": str(task.time_line_id),
            "day": str(day_of_week),
            "nbhours": str(final_hours),
            "format": "json"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(ACE_API_URL, data=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise Exception(f"Error calling ACE API: {str(e)}")

        # Check for ACE API errors
        if isinstance(data, dict) and data.get("status") == "fail":
            err = data.get("results", [{}])[0].get("ERRORDESCRIPTION", "Unknown error")
            raise Exception(f"ACE API returned error: {err}")


        return 1  # success



    def get_duration_by_log_id(self, log_id: UUID) -> dict:
        log = self.db.query(TaskLogs).filter(TaskLogs.log_id == log_id).first()

        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

        return {
            "log_id": log.log_id,
            "duration": log.duration
        }
    

    def get_latest_log(self, task_id: str, user_id: str):
        try:
            log = (
                self.db.query(TaskLogs)
                .filter(
                    TaskLogs.ace_task_id == task_id,
                    TaskLogs.user_id == UUID(user_id),
                    TaskLogs.end_time == None
                )
                .order_by(TaskLogs.start_time.desc())  # just in case multiple logs exist
                .first()
            )

            if not log:
                return {"log_id": None, "duration": 0}

            return {
                "log_id": log.log_id,
                "duration": log.duration or 0
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch latest log: {str(e)}"
            )
