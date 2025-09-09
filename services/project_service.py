import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.projects import Projects
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
ACE_API_URL = os.getenv('ACE_API_URL')

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_store_projects(self, guid: str):
        params = {
            "fct": "getprojects",
            "guid": guid,
            "format": "json"
        }

        try:
            response = requests.get(ACE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" not in data or not data["results"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No projects found"
                )

            projects_data = data["results"]

            for project in projects_data:
                existing_project = self.db.query(Projects).filter_by(project_id=str(project["PROJECT_ID"])).first()
                if not existing_project:
                    new_project = Projects(
                        project_id=str(project["PROJECT_ID"]),  # store actual project ID
                        project_name=project.get("PROJECT_NAME", ""),
                        description=project.get("PROJECT_DESC", ""),
                        start_date=self._parse_date(project.get("DATE_CREATED")),
                        end_date=self._parse_date(project.get("DATE_MODIFIED")),
                        supervisor_id=None  # You can fill this if you have mapping with Users table
                    )
                    self.db.add(new_project)

            self.db.commit()
            return {"message": "Projects fetched and stored successfully"}

        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calling ACE API: {str(e)}"
            )

    def _parse_date(self, date_str):
        if date_str:
            try:
                return datetime.fromisoformat(date_str)
            except:
                return None
        return None
