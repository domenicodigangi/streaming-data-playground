import asyncio
import logging

import uvicorn
from composer.api.time_series import router as ts_router
from composer.core.kafka_publisher import KafkaLoopPublisher
from fastapi import FastAPI

publisher = KafkaLoopPublisher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Composer data sampler is running"}


app.include_router(ts_router, prefix="/v1/time_series")


@app.post("/set_params")
async def set_params(new_mean: float, new_variance: float):
    publisher.sampler.set_params(new_mean, new_variance)
    return {"message": "Parameters updated", "mean": new_mean, "variance": new_variance}


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(publisher.publish_loop())


def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
