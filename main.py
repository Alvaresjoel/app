from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from connection.database import engine, Base
from routes.data_routes import router as data_router
from routes.user_routes import router as user_router
from routes.task_routes import router as task_router
from routes.project_routes import router as project_router
from routes.genai_routes import genai_router
from routes.auth_routes import router as auth_router
from models.users import Users
from models.projects import Projects
from models.tasks import Tasks
from models.task_assignees import TasksAssignees
from models.task_logs import TaskLogs

Base.metadata.create_all(bind=engine)
app = FastAPI()

# CORS configuration to allow frontend dev server access
origins = [
	"http://localhost:5173",
	"http://127.0.0.1:5173",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(genai_router)
app.include_router(data_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(auth_router)



