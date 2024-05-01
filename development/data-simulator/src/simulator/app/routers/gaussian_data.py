import logging

from fastapi import APIRouter

from simulator.app.routers import background_tasks_executors, start_task, stop_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gaussian_router = APIRouter()


task_name = "gaussian_sampler"
@gaussian_router.post(f"/start_task/{task_name}")
async def start_gaussian_sampler():
    return await start_task(task_name, background_tasks_executors[task_name])
@gaussian_router.post(f"/stop_task/{task_name}")
async def stop_gaussian_sampler():
    return await stop_task(task_name)


