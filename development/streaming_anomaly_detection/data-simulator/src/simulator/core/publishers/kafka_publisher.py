import logging
import subprocess
from functools import cached_property

import tenacity
from kafka import KafkaProducer
from pydantic import BaseModel

from simulator.core import load_config_yaml
from simulator.core.publishers.abstract_publisher import AbstractPeriodicMsgPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_kafka_port_from_kubectl() -> str:
    try:
        result = subprocess.run(
            ["kubectl", "get", "service", "cluster-01-kafka-external1-bootstrap",
             "-o=jsonpath='{.spec.ports[0].nodePort}{\"\\n\"}'", "-n", "kafka", ],
            capture_output=True, text=True, check=True, )
        return result.stdout.strip().strip("'")
    except Exception as e:
        raise ValueError("Failed to get Kafka port") from e


class KafkaConfig(BaseModel):
    host: str
    port: int | str
    topic: str

    @cached_property
    def bootstrap_servers(self):
        if self.port == "kubectl":
            self.port = int(get_kafka_port_from_kubectl())

        return f"{self.host}:{self.port}"


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        super().__init__()
        self._config = KafkaConfig(**load_config_yaml("kafka-config.yaml"))

        logger.info("Kafka config: %s", self._config)
        self.producer = self.get_producer()

    def publish_one(self, msg: bytes):
        logger.info("Publishing message: %s", msg)
        self.producer.send(self._config.topic, value=msg)
        self.producer.flush()


    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10))
    def get_producer(self):
        return KafkaProducer(bootstrap_servers=self._config.bootstrap_servers,
                             value_serializer=lambda v: v, )
