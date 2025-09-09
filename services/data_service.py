import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.projects import Projects
from models.tasks import Tasks
from models.task_assignees import TasksAssignees
from models.users import Users
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
ACE_API_URL = os.getenv('ACE_API_URL')

class DataService:
    def __init__(self, db: Session):
        self.db = db

    # -------- Fetch & Save Users (no GUID) --------
    def fetch_users(self, guid: str):
        params = {"fct": "getusers", "guid": guid, "format": "json"}
        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                return []

            users_data = data.get("results", []) or []
            inserted = 0

            for item in users_data:
                ace_user_id = item.get("USER_ID") or item.get("ACE_USER_ID") or item.get("ID_USER")
                email = item.get("EMAIL_ALERT") or item.get("EMAIL")
                role = item.get("ROLE") or item.get("USER_ROLE")

                if ace_user_id is None or email is None:
                    continue

                try:
                    ace_user_id_int = int(ace_user_id)
                except Exception:
                    continue

                existing = (
                    self.db.query(Users)
                    .filter((Users.ace_user_id == ace_user_id_int) | (Users.email == email))
                    .first()
                )
                if existing:
                    continue

                self.db.add(Users(ace_user_id=ace_user_id_int, email=email, role=role))
                inserted += 1

            if inserted:
                self.db.commit()

            return users_data

        except requests.RequestException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error calling ACE API: {str(e)}")

    # -------- Fetch & Save Projects --------
    def fetch_projects(self, guid: str):
        params = {"fct": "getprojects", "guid": guid, "format": "json"}
        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" not in data or not data["results"]:
                return []

            projects_data = data["results"]

            for project in projects_data:
                existing = self.db.query(Projects).filter_by(ace_project_id=project["PROJECT_ID"]).first()
                if not existing:
                    new_project = Projects(
                        ace_project_id=project["PROJECT_ID"],
                        project_name=project.get("PROJECT_NAME", ""),
                        description=project.get("PROJECT_DESC", ""),
                        start_date=self._parse_date(project.get("DATE_CREATED")),
                        end_date=self._parse_date(project.get("DATE_MODIFIED")),
                        supervisor_id=project.get("PROJECT_CREATOR_ID", "")
                    )
                    self.db.add(new_project)

            self.db.commit()
            return projects_data

        except requests.RequestException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error calling ACE API: {str(e)}")

    # -------- Fetch & Save Tasks --------
    def fetch_tasks(self, guid: str):
        params = {"fct": "gettasks", "guid": guid, "format": "json"}
        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                return []

            tasks_data = data.get("results", [])

            for task in tasks_data:
                existing = self.db.query(Tasks).filter_by(ace_task_id=task["TASK_ID"]).first()
                if not existing:
                    new_task = Tasks(
                        ace_task_id=task["TASK_ID"],
                        task_title=task.get("TASK_RESUME", ""),
                        description=task.get("TASK_DESC_CREATOR", ""),
                        ace_project_id=task["PROJECT_ID"],  # Links to Projects.ace_project_id
                        start_date=self._parse_date(task.get("DATE_TASK_CREATED")),
                        end_date=self._parse_date(task.get("DATE_TASK_MODIFIED"))
                    )
                    self.db.add(new_task)

            self.db.commit()
            return tasks_data

        except requests.RequestException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error calling ACE API: {str(e)}")

    # -------- Save Task Assignees (after tasks exist) --------
    def save_task_assignees(self, guid: str):
        params = {"fct": "gettasks", "guid": guid, "format": "json"}
        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "ok":
                return 0

            tasks_data = data.get("results", [])
            inserted = 0

            for task in tasks_data:
                ace_task_id = task.get("TASK_ID")
                if ace_task_id is None:
                    continue
                # ensure task exists to satisfy FK
                task_exists = self.db.query(Tasks).filter_by(ace_task_id=ace_task_id).first()
                if not task_exists:
                    continue

                assigned_at = self._parse_date(task.get("DATE_TASK_CREATED"))
                assigned_ids_raw = task.get("ASSIGNED_ID")

                def _parse_assignee_ids(val):
                    if val is None:
                        return []
                    if isinstance(val, int):
                        return [val]
                    if isinstance(val, str):
                        parts = [p.strip() for p in val.split(",") if p and p.strip()]
                        ids = []
                        for p in parts:
                            try:
                                ids.append(int(p))
                            except Exception:
                                continue
                        return ids
                    return []

                assignee_ids = _parse_assignee_ids(assigned_ids_raw)

                for assignee_id in assignee_ids:
                    exists_assignment = (
                        self.db.query(TasksAssignees)
                        .filter(
                            TasksAssignees.ace_task_id == ace_task_id,
                            TasksAssignees.ace_user_id == assignee_id,
                        )
                        .first()
                    )
                    if not exists_assignment:
                        self.db.add(
                            TasksAssignees(
                                ace_task_id=ace_task_id,
                                ace_user_id=assignee_id,
                                assigned_at=assigned_at,
                            )
                        )
                        inserted += 1

            if inserted:
                self.db.commit()

            return inserted
        except requests.RequestException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error calling ACE API: {str(e)}")

    # -------- Date Parser --------
    def _parse_date(self, date_str):
        if date_str:
            try:
                return datetime.fromisoformat(date_str)
            except:
                return None
        return None
