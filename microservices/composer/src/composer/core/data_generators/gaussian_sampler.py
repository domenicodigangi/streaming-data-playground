import asyncio
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.responses import JSONResponse


class GaussianSampler:
    def __init__(self, mean=0.0, variance=1.0, interval=1):
        self.mean = mean
        self.variance = variance
        self.interval = interval

    def sample_one(self):
        sampled_value = random.gauss(self.mean, self.variance**0.5)
        logger.info(f"Sampled value: {sampled_value}")
        return sampled_value

    def set_params(self, mean, variance):
        self.mean = mean
        self.variance = variance

    async def sample_loop(self):
        while True:
            sampled_value = self.sample_one()
            await asyncio.sleep(self.interval)
