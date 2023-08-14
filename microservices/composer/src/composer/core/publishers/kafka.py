import asyncio

from composer.core.data_generators.gaussian_sampler import GaussianSampler
from kafka import KafkaProducer
from pydantic import BaseModel
from composer.core.publishers.abstract_publisher import (
    AbstractPeriodicMsgPublisher,
    PublisherConfig,
)


class KafkaConfig(PublisherConfig):
    bootstrap_servers: str = "0.0.0.0:8893"
    topic: str = "topic-01"
    value_key: str = "value_01: "


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        self._config = KafkaConfig()
        self.producer = KafkaProducer(bootstrap_servers=self._config.bootstrap_servers)

    def publish_one(self, msg: bytes):
        self.producer.send(self._config.topic, key=self._config.key, value=msg)

        self.producer.flush()

    async def publish_loop(self, sampler: GaussianSampler):
        while True:
            msg = self.get_msg_from_sampler(sampler)
            self.publish_one(msg)
            await asyncio.sleep(sampler.interval)

    def get_msg_from_sampler(self, sampler: GaussianSampler) -> bytes:
        value = sampler.sample_one()
        msg_str = "{" + f"{self._config.value_key}{value}" + "}"
        return bytes(msg_str)
