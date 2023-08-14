import asyncio
import logging
import random
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GaussianSamplerParams(BaseModel):
    mean: float = 0.1
    variance: float = 1.0
    interval_sec: float = 0.5


class GaussianSampler:
    def __init__(self, params: GaussianSamplerParams | None = None):
        self._params = params or GaussianSamplerParams()

    def sample_one(self):
        sampled_value = random.gauss(self._params.mean, self._params.variance**0.5)
        logger.info(f"Sampled value: {sampled_value}")
        return sampled_value

    def set_params(self, params: GaussianSamplerParams):
        self.params = params

    async def sample_loop(self):
        while True:
            sampled_value = self.sample_one()
            await asyncio.sleep(self.params.interval)
