import asyncio
import logging
from abc import ABC
from typing import Dict

from simulator.core.data_generators.abstract_sampler import AbstractSampler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbstractPeriodicMsgPublisher(ABC):

    async def publish_loop(self, sampler: AbstractSampler):
        while True:
            msg = self.get_msg_from_sampler(sampler)
            self.publish_one(msg)
            await asyncio.sleep(sampler.params.interval_sec)

    def get_msg_from_sampler(self, sampler: AbstractSampler) -> Dict:
        msg = sampler.sample_one_msg()
        logger.debug("Sampled message: %s", msg)
        return msg

    def publish_one(self, msg: Dict):
        raise NotImplementedError()
