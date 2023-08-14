#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"

# Apply the Kafka configuration
kubectl apply -f "$SCRIPT_DIR/kafka-persistent-single.yml" -n kafka

# Wait for the Kafka cluster to be ready
kubectl wait kafka/cluster-01 --for=condition=Ready --timeout=300s -n kafka
