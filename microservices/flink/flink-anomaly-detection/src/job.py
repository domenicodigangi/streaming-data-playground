from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer


def kafka_consumer_example():
    # Create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()

    # Create a Kafka consumer
    kafka_props = {
        "bootstrap.servers": "localhost:9092",  # Adjust the address to your Kafka broker
        "group.id": "my-group",
    }

    kafka_consumer = FlinkKafkaConsumer(
        "topic-01",
        SimpleStringSchema(),
        kafka_props,
    ).set_start_from_earliest()

    # Add Kafka consumer as the data source
    ds = env.add_source(kafka_consumer)

    # Print the consumed records
    ds.print()

    # Execute job
    env.execute("Kafka Consumer Example")


if __name__ == "__main__":
    kafka_consumer_example()
