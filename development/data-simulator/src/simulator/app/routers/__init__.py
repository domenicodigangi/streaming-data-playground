import asyncio
import logging
from typing import Awaitable

from simulator.core.data_generators.gaussian_sampler import (GaussianSampler, )
# from simulator.api.time_series import router as ts_router
from simulator.core.publishers.kafka_publisher import KafkaPublisher

background_tasks_executors = {
    "gaussian_sampler": KafkaPublisher().publish_loop(GaussianSampler())
}
background_tasks = {}  # Dictionary to keep track of background_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# app.include_router(ts_router, prefix="/v1/time_series")


async def start_task(task_name: str, task:Awaitable):
    global background_tasks
    if task_name in background_tasks and not background_tasks[task_name].done():
        return {"message": f"Task {task_name} is already running"}
    elif task_name in background_tasks_executors.keys():
        background_tasks[task_name] = asyncio.create_task(
            task
        )
        return {"message": f"{task_name.capitalize()} task started"}
    # Add other background_tasks here as needed
    else:
        return {"message": f"Task {task_name} not found or not supported"}

async def stop_task(task_name: str):
    global background_tasks
    if task_name in background_tasks and not background_tasks[task_name].done():
        background_tasks[task_name].cancel()
        del background_tasks[task_name]
        return {"message": f"{task_name.capitalize()} task stopped"}
    else:
        return {"message": f"{task_name.capitalize()} task is not running"}


