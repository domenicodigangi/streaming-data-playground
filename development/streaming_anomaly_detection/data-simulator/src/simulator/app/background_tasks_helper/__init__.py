import asyncio
import logging
from typing import Coroutine, Dict

from pydantic import BaseModel

from simulator.core.data_generators.abstract_sampler import AbstractDataSourceSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskSetup(BaseModel):
    task_name: str
    executor: Coroutine
    executor_settings: AbstractDataSourceSettings

    class Config:
        arbitrary_types_allowed = True


class RunningTask(BaseModel):
    task: asyncio.Task
    task_setup: TaskSetup

    class Config:
        arbitrary_types_allowed = True


class BackgroundTasksHelper:
    RUNNING_TASKS: Dict[
        str, RunningTask] = {}  # Dictionary to keep track of RUNNING_TASKS

    @classmethod
    async def update_task(cls, task_setup: TaskSetup):
        await cls.stop_task(task_setup.task_name)
        await cls.start_task(task_setup)

    @classmethod
    async def start_task(cls, task_setup: TaskSetup):
        if (task_setup.task_name in cls.RUNNING_TASKS and not cls.RUNNING_TASKS[
            task_setup.task_name].task.done()):
            return {"message": f"Task {task_setup.task_name} is already running"}
        else:
            cls.RUNNING_TASKS[task_setup.task_name] = RunningTask(
                task=asyncio.create_task(task_setup.executor), task_setup=task_setup)
            return {"message": f"{task_setup.task_name.capitalize()} task started"}

    @classmethod
    async def stop_task(cls, task_name: str):
        if task_name in cls.RUNNING_TASKS and not cls.RUNNING_TASKS[
            task_name].task.done():
            cls.RUNNING_TASKS[task_name].task.cancel()
            del cls.RUNNING_TASKS[task_name]
            return {"message": f"{task_name.capitalize()} task stopped"}
        else:
            return {"message": f"{task_name.capitalize()} task is not running"}

    @classmethod
    async def get_task_setup(cls, task_name: str) -> TaskSetup:
        if task_name in cls.RUNNING_TASKS:
            return cls.RUNNING_TASKS[task_name].task_setup
        else:
            raise RuntimeError(f"{task_name.capitalize()} task is not running")
