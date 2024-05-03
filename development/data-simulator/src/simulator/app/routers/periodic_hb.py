import logging

from fastapi import APIRouter

from simulator.app.routers import BackgroundTasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

periodic_hb = APIRouter()


TASK_NAME = "periodic_hb"


@periodic_hb.post(f"/start_task/{TASK_NAME}")
async def start():
    return await BackgroundTasks.start_task(
        TASK_NAME,
    )


@periodic_hb.post(f"/stop_task/{TASK_NAME}")
async def stop():
    return await BackgroundTasks(TASK_NAME)
