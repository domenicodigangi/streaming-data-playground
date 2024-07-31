import logging

from fastapi import APIRouter

from simulator.app.background_tasks_helper import BackgroundTasksHelper, TaskSetup
from simulator.core.data_generators.gaussian_sampler import (GaussianSampler,
                                                             GaussianSamplerParams, )
from simulator.core.publishers.kafka_publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gaussian_router = APIRouter()

kafka_publisher = KafkaPublisher()
TASK_NAME = "gaussian_sampler"


@gaussian_router.post(f"/{TASK_NAME}/start")
async def start(params: GaussianSamplerParams | None = None):
    gaussian_sample_task = TaskSetup(task_name=TASK_NAME,
        executor=KafkaPublisher().publish_loop(GaussianSampler(params)), )
    return await BackgroundTasksHelper.start_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/update")
async def update(params: GaussianSamplerParams | None = None):
    gaussian_sample_task = TaskSetup(task_name=TASK_NAME,
        executor=kafka_publisher.publish_loop(GaussianSampler(params)), )
    return await BackgroundTasksHelper.update_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/stop")
async def stop():
    return await BackgroundTasksHelper.stop_task(TASK_NAME)
