#!/bin/bash
INIT_DIR=$(pwd)
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"



# Create the namespace if it doesn't exist
kubectl get namespace kafka || kubectl create namespace kafka

echo "Deploying Strimzi Operator..."
. "$SCRIPT_DIR/strimzi_operator_based/deploy_strimzi_operator.sh"
cd $INIT_DIR
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Applying the Kafka configuration..."
kubectl apply -f "$SCRIPT_DIR/strimzi_operator_based/kafka-ephemeral-single.yml" -n kafka
cd $INIT_DIR
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Waiting for the Kafka cluster to be ready..."

kubectl wait kafka/cluster-01 --for=condition=Ready --timeout=300s -n kafka
cd $INIT_DIR
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Creating topic..."

kubectl create -n kafka -f "$SCRIPT_DIR/strimzi_operator_based/topic-01.yml"
cd $INIT_DIR
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


echo "Forward port for kafka clients"
nohup kubectl port-forward pods/cluster-01-kafka-0 9090:9090 9091:9091 9092:9092 9093:9093 9094:9095 -n kafka  > port_forward_kafka-cluster.log || true &
cd $INIT_DIR

echo "Script execution completed."
