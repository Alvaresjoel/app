from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from connection.database import engine, Base
from routes.data_routes import router as data_router
from routes.user_routes import router as user_router
from routes.task_routes import router as task_router
from routes.genai_routes import genai_router
from routes.auth_routes import router as auth_router
from routes.agent_routes import agent_router
from routes.chat_routes import router as chat_router
from models.users import Users
from models.projects import Projects
from models.tasks import Tasks
from models.task_assignees import TasksAssignees
from models.task_logs import TaskLogs
from routes.email_routes import router as email_router
from scheduler import create_scheduler, add_jobs


Base.metadata.create_all(bind=engine)
app = FastAPI()
scheduler = create_scheduler()

@app.on_event("startup")
async def on_startup():
    add_jobs(scheduler)
    scheduler.start()
    print("Scheduler started")

@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
    print("Scheduler stopped")

# CORS configuration to allow frontend dev server access
origins = [
	"http://localhost:5173",
	"http://localhost:8000",
 	"http://127.0.0.1:8000"
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
app.include_router(agent_router)
app.include_router(email_router)
app.include_router(chat_router)
