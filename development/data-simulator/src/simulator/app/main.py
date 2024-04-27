import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from simulator.core.data_generators.gaussian_sampler import (
    GaussianSampler,
    GaussianSamplerParams,
)

# from simulator.api.time_series import router as ts_router
from simulator.core.publishers.kafka_publisher import KafkaPublisher

sampler = GaussianSampler()

background_tasks_executors = {
    "gaussian_sampler": KafkaPublisher().publish_loop(sampler)
}
background_tasks = {}  # Dictionary to keep track of background_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "simulator data sampler is running"}


# app.include_router(ts_router, prefix="/v1/time_series")


@app.post("/start_task/{task_name}")
async def start_task(task_name: str):
    global background_tasks
    if task_name in background_tasks and not background_tasks[task_name].done():
        return {"message": f"Task {task_name} is already running"}
    elif task_name in background_tasks_executors.keys():
        background_tasks[task_name] = asyncio.create_task(
            background_tasks_executors[task_name]
        )
        return {"message": f"{task_name.capitalize()} task started"}
    # Add other background_tasks here as needed
    else:
        return {"message": f"Task {task_name} not found or not supported"}


@app.post("/stop_task/{task_name}")
async def stop_task(task_name: str):
    global background_tasks
    if task_name in background_tasks and not background_tasks[task_name].done():
        background_tasks[task_name].cancel()
        del background_tasks[task_name]
        return {"message": f"{task_name.capitalize()} task stopped"}
    else:
        return {"message": f"{task_name.capitalize()} task is not running"}


def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
