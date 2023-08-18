import asyncio

from simulator.core.data_generators.gaussian_sampler import GaussianSampler
from kafka import KafkaProducer
from pydantic import BaseModel
from simulator.core.publishers.abstract_publisher import (
    AbstractPeriodicMsgPublisher,
    PublisherConfig,
)


class KafkaConfig(PublisherConfig):
    bootstrap_servers: str = "0.0.0.0:9092"
    topic: str = "topic-01"
    value_key: str = "value_01: "


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        self._config = KafkaConfig()
        self.producer = KafkaProducer(bootstrap_servers=self._config.bootstrap_servers)

    def publish_one(self, msg: bytes):
        self.producer.send(self._config.topic, key=self._config.value_key, value=msg)

        self.producer.flush()
