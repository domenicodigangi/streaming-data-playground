import logging
from pydantic import BaseModel
from confluent_kafka import Producer

class KafkaConfig(BaseModel):
    bootstrap_servers: str = "10.244.0.7:9092"
    topic_name: str = "topic-01"

    class Config:
        env_prefix = "KAFKA_"

class EventPublisher:
    def __init__(self, target="print"):
        self.target = target
        self.kafka_config = KafkaConfig()
        self.logger = logging.getLogger("EventPublisher")  # Create a logger instance

    def emit(self, timestamp, value):
        if self.target == "kafka":
            self._publish_to_kafka(timestamp, value)
        elif self.target == "rabbitmq":
            self._publish_to_rabbitmq(timestamp, value)
        else:
            self.logger.info(f"Timestamp: {timestamp}, Value: {value}")

    def _publish_to_kafka(self, timestamp, value):
        def delivery_report(err, msg):
            if err is not None:
                self.logger.error(f"Message delivery failed: {err}")
            else:
                self.logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        producer = Producer({'bootstrap.servers': self.kafka_config.bootstrap_servers})
        producer.produce(self.kafka_config.topic_name, key=str(timestamp), value=str(value), callback=delivery_report)
        producer.flush()

    def _publish_to_rabbitmq(self, timestamp, value):
        # TODO: Add code to publish to RabbitMQ
        self.logger.info(f"Publishing to RabbitMQ -> Timestamp: {timestamp}, Value: {value}")

# Configure the logging format and level
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if __name__ == "__main__":
    publisher = EventPublisher(target="kafka")
    publisher.emit("2023-08-10", "Some message")
