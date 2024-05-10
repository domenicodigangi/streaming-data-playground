import asyncio
import logging
from typing import Coroutine

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskSetup(BaseModel):
    task_name: str
    executor: Coroutine

    class Config:
        arbitrary_types_allowed = True


class BackgroundTasksHelper:

    RUNNING_TASKS = {}  # Dictionary to keep track of RUNNING_TASKS

    @classmethod
    async def update_task(cls, task_setup: TaskSetup):
        await cls.stop_task(task_setup.task_name)
        await cls.start_task(task_setup)

    @classmethod
    async def start_task(cls, task_setup: TaskSetup):
        if (
            task_setup.task_name in cls.RUNNING_TASKS
            and not cls.RUNNING_TASKS[task_setup.task_name].done()
        ):
            return {"message": f"Task {task_setup.task_name} is already running"}
        else:
            cls.RUNNING_TASKS[task_setup.task_name] = asyncio.create_task(
                task_setup.executor
            )
            return {"message": f"{task_setup.task_name.capitalize()} task started"}

    @classmethod
    async def stop_task(cls, task_name: str):
        if task_name in cls.RUNNING_TASKS and not cls.RUNNING_TASKS[task_name].done():
            cls.RUNNING_TASKS[task_name].cancel()
            del cls.RUNNING_TASKS[task_name]
            return {"message": f"{task_name.capitalize()} task stopped"}
        else:
            return {"message": f"{task_name.capitalize()} task is not running"}
