import logging

from fastapi import APIRouter
from simulator.app.background_tasks_helper import BackgroundTasksHelper, TaskSetup
from simulator.core.data_generators.gaussian_sampler import (
    GaussianSampler,
    GaussianSamplerParams,
)
from simulator.core.publishers.kafka_publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gaussian_router = APIRouter()


TASK_NAME = "gaussian_sampler"


@gaussian_router.post(f"/{TASK_NAME}/start/"+"{item_id}")
async def start(item_id:int, params: GaussianSamplerParams | None = None):
    gaussian_sample_task = TaskSetup(
        task_name=f"{TASK_NAME}_{item_id}",
        executor=KafkaPublisher().publish_loop(GaussianSampler(params)),
    )
    return await BackgroundTasksHelper.start_task(
        gaussian_sample_task,
    )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/update")
async def update(item_id:int, params: GaussianSamplerParams | None = None):
    gaussian_sample_task = TaskSetup(
        task_name=f"{TASK_NAME}_{item_id}",
        executor=KafkaPublisher().publish_loop(GaussianSampler(params)),
    )
    return await BackgroundTasksHelper.update_task(
        gaussian_sample_task,
    )


@gaussian_router.post(f"/{TASK_NAME}/{{item_id}}/stop")
async def stop(item_id:int):
    return await BackgroundTasksHelper.stop_task(TASK_NAME)
