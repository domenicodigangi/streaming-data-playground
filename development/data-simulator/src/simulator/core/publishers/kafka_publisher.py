import logging
import subprocess

import tenacity
from kafka import KafkaProducer
from pydantic import BaseModel
from simulator.core.publishers.abstract_publisher import (
    AbstractPeriodicMsgPublisher,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConfig(BaseModel):
    @staticmethod
    def get_kafka_port():
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "service",
                    "cluster-01-kafka-external1-bootstrap",
                    "-o=jsonpath='{.spec.ports[0].nodePort}{\"\\n\"}'",
                    "-n",
                    "kafka",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip().strip("'")
        except Exception as e:
            raise ValueError("Failed to get Kafka port") from e

    # Update the following using the minikube cluster IP from `minikube ip`
    bootstrap_servers: str = f"192.168.49.2:{get_kafka_port()}"
    topic: str = "topic-01"


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        super().__init__()
        self._config = KafkaConfig()
        logger.info("Kafka config: %s", self._config)
        self.producer = self.get_producer()

    def publish_one(self, msg: bytes):
        logger.info("Publishing message: %s", msg)
        self.producer.send(self._config.topic, value=msg)
        self.producer.flush()
        self.producer.send(self._config.topic, value=msg)
        self.producer.flush()

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10))
    def get_producer(self):
        return KafkaProducer(
            bootstrap_servers=self._config.bootstrap_servers,
            value_serializer=lambda v: v,
        )
