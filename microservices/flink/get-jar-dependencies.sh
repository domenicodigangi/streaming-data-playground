#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"

# Define variables
FLINK_VERSION="1.15.2"  # Replace with the version you need

# Download Kafka connector JAR
wget -O flink-sql-connector-kafka-${FLINK_VERSION}.jar "https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/${FLINK_VERSION}/flink-sql-connector-kafka-${FLINK_VERSION}.jar"

# Move JAR to Flink's lib folder
mv flink-sql-connector-kafka-${FLINK_VERSION}.jar $SCRIPT_DIR/jar-dependencies/
