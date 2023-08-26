import asyncio
import logging
from simulator.core.data_generators.gaussian_sampler import GaussianSampler
from kafka import KafkaProducer
from pydantic import BaseModel
from simulator.core.publishers.abstract_publisher import (
    AbstractPeriodicMsgPublisher,
    PublisherConfig,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConfig(PublisherConfig):
    # update the following using the minikube cluster ip from minikube ip and the port from  kubectl get service cluster-01-kafka-external1-bootstrap -o=jsonpath='{.spec.ports[0].nodePort}{"\n"}' -n kafka
    bootstrap_servers: str = "192.168.49.2:30349"
    topic: str = "topic-01"


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        self._config = KafkaConfig()
        self.producer = KafkaProducer(bootstrap_servers=self._config.bootstrap_servers)

    def publish_one(self, msg: bytes):
        logger.info(f"Publishing message: {msg}")
        self.producer.send(self._config.topic, value=msg)
        self.producer.flush()
