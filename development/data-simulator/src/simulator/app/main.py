import asyncio
import logging

import uvicorn

# from simulator.api.time_series import router as ts_router
from simulator.core.publishers.kafka_publisher import KafkaPublisher
from simulator.core.data_generators.gaussian_sampler import (
    GaussianSampler,
    GaussianSamplerParams,
)
from fastapi import FastAPI

sampler = GaussianSampler()
publisher = KafkaPublisher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "simulator data sampler is running"}


# app.include_router(ts_router, prefix="/v1/time_series")


@app.post("/set_params")
async def set_params(new_params: GaussianSamplerParams):
    sampler.set_params(new_params)
    return {"message": f"Parameters updated to {new_params}"}


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(publisher.publish_loop(sampler))


def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
