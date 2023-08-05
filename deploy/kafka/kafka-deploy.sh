#!/bin/bash

# Variables
NAMESPACE="default"
KAFKA_DEPLOYMENT_NAME="kafka"
KAFKA_UI_DEPLOYMENT_NAME="kafka-ui"
KAFKA_TOPIC_NAME="topic-01"

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts


# Check if the service already exists
if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_DEPLOYMENT_NAME; then
    echo "Service '$KAFKA_DEPLOYMENT_NAME' is already running."
else
    echo "Service '$KAFKA_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_DEPLOYMENT_NAME bitnami/kafka --version 22.0.1 --set topics[0].name=topic-1,topics[0].partitions=1,topics[0].replicationFactor=2 -n $NAMESPACE
fi

# Check if the service already exists
if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_UI_DEPLOYMENT_NAME; then
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is already running."
else
    echo "Service '$KAFKA_UI_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_UI_DEPLOYMENT_NAME kafka-ui/kafka-ui --version 0.7.2 -f /workspaces/streaming-anomaly-detection/deploy/kafka/kafka-ui-conf.yml -n $NAMESPACE
fi

kubectl apply -f /workspaces/streaming-anomaly-detection/deploy/kafka/kafka-ui-service.yml
# Set up port forwarding for kafka-ui
nohup kubectl port-forward -n $NAMESPACE deployment/$KAFKA_UI_DEPLOYMENT_NAME 3001:8080 || true &


## TO run in producer pod
# /opt/bitnami/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_SERVER_PATH --producer.config /opt/bitnami/kafka/config/producer.properties --topic $KAFKA_TOPIC_NAME
