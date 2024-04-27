import asyncio
import logging
from abc import ABC

from pydantic import BaseModel
from simulator.core.data_generators.abstract_sampler import AbstractSampler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublisherConfig(BaseModel):
    value_key: str = '"value_01": '


class AbstractPeriodicMsgPublisher(ABC):
    def __init__(self):
        self._config = PublisherConfig()

    async def publish_loop(self, sampler: AbstractSampler):
        while True:
            msg = self.get_msg_from_sampler(sampler)
            self.publish_one(msg)
            await asyncio.sleep(sampler.params.interval_sec)

    def get_msg_from_sampler(self, sampler: AbstractSampler) -> bytes:
        value = sampler.sample_one()
        msg_str = '{"source_id": 0, ' + f"{self._config.value_key}{value}" + "}"
        return msg_str.encode("utf-8")

    def publish_one(self, msg: bytes):
        raise NotImplementedError()
