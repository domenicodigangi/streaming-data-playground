import json
import logging
import subprocess
from functools import cached_property
from typing import Dict, List

import tenacity
from kafka import KafkaProducer
from pydantic import BaseModel

from simulator.core import load_config_yaml, setup_logger
from simulator.core.publishers.abstract_publisher import AbstractPeriodicMsgPublisher

logger = setup_logger(__name__, level=logging.INFO)


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

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=10))
    def _create_producer_pool(self) -> List[KafkaProducer]:
        return [KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                              value_serializer=lambda v: v) for _ in
                range(self.pool_size)]

    def get_producer(self) -> KafkaProducer:
        producer = self.producers.pop(0)
        return producer

    def put_producer(self, producer: KafkaProducer):
        self.producers.append(producer)


class KafkaPublisher(AbstractPeriodicMsgPublisher):
    __producer_pool = None
    __config: KafkaConfig | None = None

    def __init__(self):
        super().__init__()
        self.__init_class_conn_pool()

    @classmethod
    def __init_class_conn_pool(cls):
        if cls.__producer_pool is None:
            cls.__set_kafka_config()
            cls.__producer_pool = KafkaProducerPool(
                bootstrap_servers=cls.__config.bootstrap_servers)

    @classmethod
    def __set_kafka_config(cls):
        if cls.__config is None:
            config_dict = load_config_yaml("config.yaml")
            cls.__config = KafkaConfig(**config_dict)
            logger.info("Kafka config: %s", cls.__config)

    def publish_one(self, msg: Dict, source_id_as_key: bool = True):
        msg_str = self._format_msg(msg)
        key = self._get_key(msg, source_id_as_key)
        self._produce_msg_using_pool(msg_str, key)

    def _format_msg(self, msg: Dict) -> bytes:
        return json.dumps(msg).encode("utf-8")

    def _get_key(self, msg: Dict, source_id_as_key: bool) -> bytes:
        if source_id_as_key:
            return msg["source_id"].encode("utf-8")

    def _produce_msg_using_pool(self, msg_str: bytes, key: bytes):
        logger.info("Publishing message: %s, with key %s", msg_str, key)
        producer = self.__producer_pool.get_producer()
        producer.send(self.__config.topic, value=msg_str, key=key)
        producer.flush()
        self.__producer_pool.put_producer(producer)
