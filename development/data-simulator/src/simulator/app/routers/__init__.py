import asyncio
import logging
from typing import Coroutine

from simulator.core.data_generators.gaussian_sampler import (
    GaussianSampler,
)

from simulator.core.publishers.kafka_publisher import KafkaPublisher


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackgroundTasks:
    EXECUTORS: dict[str, Coroutine] = {
        "gaussian_sampler": KafkaPublisher().publish_loop(GaussianSampler())
    }

    RUNNING_TASKS = {}  # Dictionary to keep track of RUNNING_TASKS

    @classmethod
    async def start_task(cls, task_name: str):
        if task_name in cls.RUNNING_TASKS and not cls.RUNNING_TASKS[task_name].done():
            return {"message": f"Task {task_name} is already running"}
        elif task_name in cls.EXECUTORS:
            cls.RUNNING_TASKS[task_name] = asyncio.create_task(cls.EXECUTORS[task_name])
            return {"message": f"{task_name.capitalize()} task started"}
        # Add other RUNNING_TASKS here as needed
        else:
            return {"message": f"Task {task_name} not found or not supported"}

    @classmethod
    async def stop_task(cls, task_name: str):
        if task_name in cls.RUNNING_TASKS and not cls.RUNNING_TASKS[task_name].done():
            cls.RUNNING_TASKS[task_name].cancel()
            del cls.RUNNING_TASKS[task_name]
            return {"message": f"{task_name.capitalize()} task stopped"}
        else:
            return {"message": f"{task_name.capitalize()} task is not running"}
