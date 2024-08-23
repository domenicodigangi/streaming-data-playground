import json
import logging
import subprocess
from functools import cached_property
from typing import Dict, List

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


class KafkaProducerPool:
    def __init__(self, bootstrap_servers: str, pool_size: int = 5):
        self.bootstrap_servers = bootstrap_servers
        self.pool_size = pool_size
        self.producers = self._create_producer_pool()

    def _create_producer_pool(self) -> List[KafkaProducer]:
        return [KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                              value_serializer=lambda v: v) for _ in
                range(self.pool_size)]

    def get_producer(self) -> KafkaProducer:
        # Simple round-robin mechanism
        producer = self.producers.pop(0)
        self.producers.append(producer)
        return producer


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    _producer_pool = None

    def __init__(self):
        super().__init__()
        self._config = KafkaConfig(**load_config_yaml("kafka-config.yaml"))

        logger.info("Kafka config: %s", self._config)
        if KafkaPublisher._producer_pool is None:
            KafkaPublisher._producer_pool = KafkaProducerPool(
                bootstrap_servers=self._config.bootstrap_servers)

        self.producer = self.get_producer()

    def publish_one(self, msg: Dict, source_id_as_key: bool = True):
        if source_id_as_key:
            key = msg["source_id"].encode("utf-8")
        else:
            key = None
        msg_str = json.dumps(msg).encode("utf-8")
        logger.info("Publishing message: %s, with key %s", msg_str, key)
        self.producer.send(self._config.topic, value=msg_str, key=key)
        self.producer.flush()

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10))
    def get_producer(self):
        return KafkaPublisher._producer_pool.get_producer()
