import logging
import re

from fastapi import APIRouter, HTTPException, Path, status

from simulator.app.background_tasks_helper import BackgroundTasksHelper, TaskSetup
from simulator.core.data_generators.anomalies import AnomalyDefinition, AnomalyHelper
from simulator.core.data_generators.gaussian_sampler import (GaussianDataSourceSettings,
                                                             GaussianSampler,
                                                             GaussianSamplerParams, )
from simulator.core.publishers.kafka_publisher import KafkaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gaussian_router = APIRouter()

TASK_NAME = "gaussian_sampler"

# Security: Pattern for valid sampler IDs (alphanumeric, hyphens, underscores only)
# This prevents injection attacks and path traversal
VALID_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,50}$')


def validate_item_id(item_id: str) -> str:
    """Validate and sanitize item_id to prevent injection attacks.

    Args:
        item_id: The sampler ID provided by user

    Returns:
        str: Validated item_id

    Raises:
        HTTPException: If item_id is invalid
    """
    if not VALID_ID_PATTERN.match(item_id):
        logger.warning(f"Invalid item_id attempted: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item_id. Must be 1-50 characters, alphanumeric with hyphens/underscores only."
        )
    return item_id


def get_task_name(item_id: str) -> str:
    """Generate task name from validated item_id."""
    return f"{TASK_NAME}_{item_id}"


@gaussian_router.post(f"/{TASK_NAME}/start/" + "{item_id}")
async def start(
    item_id: str = Path(..., description="Unique sampler identifier", min_length=1, max_length=50),
    params: GaussianSamplerParams | None = None
):
    """Start a new Gaussian data sampler.

    Security:
        - item_id is validated to prevent injection
        - All parameters validated by Pydantic models
    """
    # Security: Validate item_id
    item_id = validate_item_id(item_id)

    source_settings = GaussianDataSourceSettings(sampler_id=item_id, params=params)
    gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
                                     executor=KafkaPublisher().publish_loop(
                                         GaussianSampler(source_settings)),
                                     executor_settings=source_settings)
    return await BackgroundTasksHelper.start_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/update")
async def update(
    item_id: str = Path(..., description="Sampler identifier to update", min_length=1, max_length=50),
    params: GaussianSamplerParams | None = None
):
    """Update parameters of a running Gaussian sampler.

    Security:
        - item_id is validated to prevent injection
        - All parameters validated by Pydantic models
    """
    # Security: Validate item_id
    item_id = validate_item_id(item_id)

    source_settings = GaussianDataSourceSettings(sampler_id=item_id, params=params)
    gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
                                     executor=KafkaPublisher().publish_loop(
                                         GaussianSampler(source_settings)),
                                     executor_settings=source_settings)
    return await BackgroundTasksHelper.update_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/anomaly")
async def anomaly(
    item_id: str = Path(..., description="Sampler identifier for anomaly injection", min_length=1, max_length=50),
    anomaly: AnomalyDefinition
):
    """Inject an anomaly pattern into a running sampler.

    Security:
        - item_id is validated to prevent injection
        - Anomaly values validated by Pydantic (exactly 20 values)
        - n_observations must be positive integer
    """
    # Security: Validate item_id
    item_id = validate_item_id(item_id)

    helper = AnomalyHelper(anomaly)
    task_setup = await BackgroundTasksHelper.get_task_setup(get_task_name(item_id))
    new_source_settings = task_setup.executor_settings.model_copy(
        update={"initial_additive_delta_list": helper.generate_list_to_add()})
    gaussian_sample_task = TaskSetup(task_name=get_task_name(item_id),
                                     executor=KafkaPublisher().publish_loop(
                                         GaussianSampler(new_source_settings)),
                                     executor_settings=new_source_settings)
    return await BackgroundTasksHelper.update_task(gaussian_sample_task, )


@gaussian_router.post(f"/{TASK_NAME}/" + "{item_id}/stop")
async def stop(
    item_id: str = Path(..., description="Sampler identifier to stop", min_length=1, max_length=50)
):
    """Stop a running Gaussian sampler.

    Security:
        - item_id is validated to prevent injection
    """
    # Security: Validate item_id
    item_id = validate_item_id(item_id)

    await BackgroundTasksHelper.stop_task(get_task_name(item_id))
