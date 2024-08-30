import logging

from fastapi import APIRouter

from simulator.app.background_tasks_helper import BackgroundTasksHelper, TaskSetup
from simulator.core.data_generators.gaussian_sampler import (GaussianDataSourceSettings,
                                                             GaussianSampler,
                                                             GaussianSamplerParams, )
from simulator.core.publishers.kafka_publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gaussian_router = APIRouter()

TASK_NAME = "gaussian_sampler"


def get_task_name(item_id: str) -> str:
    return f"{TASK_NAME}_{item_id}"


@gaussian_router.post(f"/{TASK_NAME}/start/" + "{item_id}")
async def start(item_id: str, params: GaussianSamplerParams | None = None):
    source_settings = GaussianDataSourceSettings(sampler_id=item_id, params=params)
    gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
                                     executor=KafkaPublisher().publish_loop(
                                         GaussianSampler(source_settings)), )
    return await BackgroundTasksHelper.start_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/update")
async def update(item_id: str, params: GaussianSamplerParams | None = None):
    source_settings = GaussianDataSourceSettings(sampler_id=item_id, params=params)
    gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
                                     executor=KafkaPublisher().publish_loop(
                                         GaussianSampler(source_settings)), )
    return await BackgroundTasksHelper.update_task(gaussian_sample_task, )


# @gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/anomaly")
# async def anomaly(item_id: str, params: GaussianSamplerParams | None = None):
#     source_settings = GaussianDataSourceSettings(sampler_id=item_id, params=params)
#     gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
#                                      executor=KafkaPublisher().publish_loop(
#                                          GaussianSampler(source_settings)), )
#     return await BackgroundTasksHelper.update_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/stop")
async def stop(item_id: str):
    await BackgroundTasksHelper.stop_task(get_task_name(item_id))
