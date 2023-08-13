import asyncio

from composer.core.data_generators.gaussian_sampler import GaussianSampler
from composer.core.kafka import KafkaConfig
from kafka import KafkaProducer


class KafkaLoopPublisher:
    def __init__(self, sampler: GaussianSampler):
        self.sampler = sampler
        self._config = KafkaConfig()
        self.producer = KafkaProducer(bootstrap_servers=self._config.bootstrap_servers)

    def _publish_one(self):
        msg = self.sampler.sample_one()
        self.producer.send(self._config.topic, key=self._config.key, value=msg)

        self.producer.flush()

    async def publish_loop(self):
        while True:
            self._publish_one()
            await asyncio.sleep(self.sampler.interval)
