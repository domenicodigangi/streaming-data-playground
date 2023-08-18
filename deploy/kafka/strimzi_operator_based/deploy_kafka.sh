#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"

echo "Delete kafka namespace"
kubectl wait --for=delete namespace/kafka --timeout=120s


echo "Deploying Strimzi Operator..."
. "$SCRIPT_DIR/deploy_strimzi_operator.sh"

echo "Applying the Kafka configuration..."
kubectl apply -f "$SCRIPT_DIR/kafka-ephemeral-single.yml" -n kafka

echo "Waiting for the Kafka cluster to be ready..."
kubectl wait kafka/cluster-01 --for=condition=Ready --timeout=300s -n kafka

echo "Creating topic..."
kubectl create -n kafka -f "$SCRIPT_DIR/topic-01.yml"

echo "Script execution completed."
