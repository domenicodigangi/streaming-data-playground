import logging

from fastapi import APIRouter
from simulator.app.background_tasks_helper import BackgroundTasksHelper, TaskSetup
from simulator.core.data_generators.round_robin_sampler import (
    RoundRobinSampler,
    RoundRobinSamplerParams,
)
from simulator.core.publishers.kafka_publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

periodic_hb = APIRouter()


TASK_NAME = "periodic_hb"


@periodic_hb.post(f"/{TASK_NAME}/start_task")
async def start(params: RoundRobinSamplerParams | None = None):
    periodic_hb_task = TaskSetup(
        task_name=TASK_NAME,
        executor=KafkaPublisher().publish_loop(RoundRobinSampler(params)),
    )

    return await BackgroundTasksHelper.start_task(
        periodic_hb_task,
    )


@periodic_hb.post(f"/{TASK_NAME}/update_task")
async def update(params: RoundRobinSamplerParams | None = None):
    periodic_hb_task = TaskSetup(
        task_name=TASK_NAME,
        executor=KafkaPublisher().publish_loop(RoundRobinSampler(params)),
    )

    return await BackgroundTasksHelper.update_task(
        periodic_hb_task,
    )


@periodic_hb.post(f"/{TASK_NAME}/stop_task")
async def stop():
    return await BackgroundTasksHelper.stop_task(TASK_NAME)
