#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"

# Variables
NAMESPACE="kafka"
KAFKA_UI_DEPLOYMENT_NAME="kafka-ui"
KAFKA_TOPIC_NAME="topic-01"

 

# Check if the service already exists
if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_UI_DEPLOYMENT_NAME; then
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is already running."
else
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_UI_DEPLOYMENT_NAME kafka-ui/kafka-ui --version 0.7.2 -f "$SCRIPT_DIR/kafka-ui-conf.yml" -n $NAMESPACE
fi

kubectl apply -f "$SCRIPT_DIR/kafka-ui-service.yml"
# Set up port forwarding for kafka-ui
nohup kubectl port-forward -n $NAMESPACE deployment/$KAFKA_UI_DEPLOYMENT_NAME 3001:8080 || true &
 
