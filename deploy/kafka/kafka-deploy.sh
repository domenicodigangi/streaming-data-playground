#!/bin/bash

# Variables
NAMESPACE="default"
KAFKA_DEPLOYMENT_NAME="kafka"
KAFKA_TOPIC_NAME="topic-01"

## Kafka
helm repo add bitnami https://charts.bitnami.com/bitnami


# Check if the service already exists
if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_DEPLOYMENT_NAME; then
    echo "Service '$KAFKA_DEPLOYMENT_NAME' is already running."
else
    echo "Service '$KAFKA_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_DEPLOYMENT_NAME bitnami/kafka --version 22.0.1 --set topics[0].name=topic-1,topics[0].partitions=3,topics[0].replicationFactor=2
fi
