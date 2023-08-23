#!/bin/bash
INIT_DIR=$(pwd)
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"

# Variables
NAMESPACE="kafka"
KAFKA_UI_DEPLOYMENT_NAME="kafka-ui"
KAFKA_TOPIC_NAME="topic-01"

echo "Adding Kafka UI Helm repository..."
helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts

# Check if the service already exists
if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_UI_DEPLOYMENT_NAME; then
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is already running. Upgrading it..."
    helm upgrade $KAFKA_UI_DEPLOYMENT_NAME kafka-ui/kafka-ui --version 0.7.2 -f "$SCRIPT_DIR/helm_based_ui/kafka-ui-conf.yml" -n $NAMESPACE
else
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_UI_DEPLOYMENT_NAME kafka-ui/kafka-ui --version 0.7.2 -f "$SCRIPT_DIR/helm_based_ui/kafka-ui-conf.yml" -n $NAMESPACE
fi
cd $INIT_DIR
echo "Applying Kafka UI service configuration..."
kubectl apply -f "$SCRIPT_DIR/helm_based_ui/kafka-ui-service.yml"

echo "Setting up port forwarding for Kafka UI..."
lsof -t -i :3001 | xargs kill || true
nohup kubectl port-forward -n $NAMESPACE deployment/$KAFKA_UI_DEPLOYMENT_NAME 3031:8080 > port_forward_kafka-ui.log || true &
cd $INIT_DIR
echo "Script execution completed."
