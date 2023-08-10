from composer.core.kafka import KafkaConfig
from kafka import KafkaProducer


# Send two messages to the 'test' topic
producer.send('topic-01', key=b'key', value=b'value2')

producer.flush()
producer.close()

class EventPublisher:
    def __init__(self, target="print"):
        self.target = target
        self.kafka_config = KafkaConfig()
        self.kakaproducer = KafkaProducer(bootstrap_servers=self.kafka_config.bootstrap_servers)

    def emit(self, timestamp, value):
        if self.target == "kafka":
            self._publish_to_kafka(timestamp, value)
        elif self.target == "rabbitmq":
            self._publish_to_rabbitmq(timestamp, value)
        else:
            print(f"Timestamp: {timestamp}, Value: {value}")

    def _publish_to_kafka(self, timestamp, value):
        def delivery_report(err, msg):
            if err is not None:
                print(f"Message delivery failed: {err}")
            else:
                print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

        producer.produce(self.kafka_config.topic_name, key=str(timestamp), value=str(value), callback=delivery_report)
        producer.flush()

    def _publish_to_rabbitmq(self, timestamp, value):
        # TODO: Add code to publish to RabbitMQ
        print(f"Publishing to RabbitMQ -> Timestamp: {timestamp}, Value: {value}")

