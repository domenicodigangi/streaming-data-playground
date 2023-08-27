from pyflink.common.serialization import JsonRowDeserializationSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common import Configuration
from typing import Union
import os
from pyflink.common.typeinfo import Types

JAR_DEP_FOLDER = (
    "/workspaces/streaming-anomaly-detection/microservices/flink/jar-dependencies"
)


def add_jars_in_folder_to_flink_env(
    env: StreamExecutionEnvironment, folder_path: Union[str, os.PathLike]
) -> None:
    jar_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".jar"):
            jar_files.append(f"file://{os.path.join(folder_path, filename)}")

    if jar_files:
        env.add_jars(*jar_files)


def kafka_consumer_example():
    # Create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()

    # Call the function to add all JAR files in the given folder
    add_jars_in_folder_to_flink_env(env, JAR_DEP_FOLDER)

    # Create a Kafka consumer
    kafka_props = {
        "bootstrap.servers": "192.168.49.2:30818",  # Adjust the address to your Kafka broker
        "group.id": "my-group",
    }
    deserialization_schema = (
        JsonRowDeserializationSchema.builder()
        .type_info(type_info=Types.ROW([Types.DOUBLE()]))
        .build()
    )

    kafka_consumer = FlinkKafkaConsumer(
        "topic-01",
        deserialization_schema,
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
