from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime
from models.task_logs import TaskLogs
from models.tasks import Tasks
from dependencies.get_db import get_db
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
AUTO_STOP_DURATION= float(os.getenv("AUTO_STOP_DURATION_SECONDS", 10800))

def create_scheduler():
    return AsyncIOScheduler()

async def auto_stop_tasks():
    # Get DB session
    db: Session = next(get_db())

    # Find logs that are still active (no end_time)
    active_logs = db.query(TaskLogs).filter(TaskLogs.end_time.is_(None)).all()

    for log in active_logs:
        log.end_time = datetime.now()
        log.status = "In progress"
        log.comment = "Stopped automatically by system scheduler"
        log.duration = AUTO_STOP_DURATION 

        # Update task status as well
        task = db.query(Tasks).filter(Tasks.ace_task_id == log.ace_task_id).first()
        if task:
            task.status = "In progress"
            task.end_date = datetime.now()

    db.commit()
    db.close()

def add_jobs(scheduler: AsyncIOScheduler):
    trigger = CronTrigger(hour=12, minute=55)
    scheduler.add_job(auto_stop_tasks, trigger, id="auto_stop_tasks", replace_existing=True)
