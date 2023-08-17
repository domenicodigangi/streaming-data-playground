import asyncio
import logging
from composer.core.data_generators.gaussian_sampler import GaussianSampler
from kafka import KafkaProducer
from pydantic import BaseModel
from abc import ABC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublisherConfig(BaseModel):
    value_key: str = "value_01: "


class AbstractPeriodicMsgPublisher(ABC):
    def __init__(self):
        self._config = PublisherConfig()

    async def publish_loop(self, sampler: GaussianSampler):
        while True:
            msg = self.get_msg_from_sampler(sampler)
            self.publish_one(msg)
            await asyncio.sleep(sampler.interval)

    def get_msg_from_sampler(self, sampler: GaussianSampler) -> bytes:
        value = sampler.sample_one()
        msg_str = "{" + f"{self._config.value_key}{value}" + "}"
        return bytes(msg_str)

    def publish_one(self, msg: bytes):
        raise NotImplementedError()
