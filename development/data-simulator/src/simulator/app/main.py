import logging

import uvicorn
from fastapi import FastAPI

from simulator.app.routers.gaussian_data import gaussian_router
from simulator.core.data_generators.gaussian_sampler import (GaussianSampler, )
# from simulator.api.time_series import router as ts_router
from simulator.core.publishers.kafka_publisher import KafkaPublisher

background_tasks_executors = {
    "gaussian_sampler": KafkaPublisher().publish_loop(GaussianSampler())
}
background_tasks = {}  # Dictionary to keep track of background_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "simulator data sampler is running"}


app.include_router(gaussian_router, prefix="/v1/gaussian")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
