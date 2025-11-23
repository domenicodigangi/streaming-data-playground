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
    """Get Kafka port from kubectl service.

    Raises:
        ValueError: If kubectl command fails or service not found
    """
    try:
        result = subprocess.run(
            ["kubectl", "get", "service", "cluster-01-kafka-external1-bootstrap",
             "-o=jsonpath='{.spec.ports[0].nodePort}{\"\\n\"}'", "-n", "kafka", ],
            capture_output=True, text=True, check=True, timeout=10)
        port = result.stdout.strip().strip("'")
        if not port:
            raise ValueError("Empty port returned from kubectl")
        return port
    except subprocess.TimeoutExpired as e:
        logger.error("Kubectl command timed out")
        raise ValueError("Kubectl command timed out after 10 seconds") from e
    except subprocess.CalledProcessError as e:
        logger.error(f"Kubectl command failed: {e.stderr}")
        raise ValueError(f"Failed to get Kafka port from kubectl: {e.stderr}") from e
    except Exception as e:
        logger.error(f"Unexpected error getting Kafka port: {e}")
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

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True
    )
    def _create_producer_pool(self) -> List[KafkaProducer]:
        """Create a pool of Kafka producers with retry logic.

        Returns:
            List of KafkaProducer instances

        Raises:
            Exception: If producers cannot be created after retries
        """
        try:
            logger.info(f"Creating Kafka producer pool (size={self.pool_size}) for {self.bootstrap_servers}")
            producers = [
                KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: v,
                    retries=3,
                    max_in_flight_requests_per_connection=1,
                    acks='all'
                ) for _ in range(self.pool_size)
            ]
            logger.info(f"Successfully created {len(producers)} Kafka producers")
            return producers
        except Exception as e:
            logger.error(f"Failed to create Kafka producer pool: {e}", exc_info=True)
            raise

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

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        stop=tenacity.stop_after_attempt(3),
        reraise=True
    )
    def _produce_msg_using_pool(self, msg_str: bytes, key: bytes):
        """Publish a message to Kafka with retry logic.

        Args:
            msg_str: Serialized message bytes
            key: Message key bytes

        Raises:
            Exception: If message cannot be published after retries
        """
        logger.debug("Publishing message with key %s to topic %s", key, self.__config.topic)
        producer = None
        try:
            producer = self.__producer_pool.get_producer()
            future = producer.send(self.__config.topic, value=msg_str, key=key)
            # Wait for the send to complete to catch errors early
            record_metadata = future.get(timeout=10)
            producer.flush()
            logger.debug(
                f"Message published successfully: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )
        except Exception as e:
            logger.error(f"Failed to publish message to Kafka: {e}", exc_info=True)
            raise
        finally:
            if producer:
                self.__producer_pool.put_producer(producer)
