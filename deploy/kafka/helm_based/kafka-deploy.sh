#!/bin/bash

# Variables
NAMESPACE="default"
KAFKA_DEPLOYMENT_NAME="kafka"
KAFKA_UI_DEPLOYMENT_NAME="kafka-ui"
KAFKA_TOPIC_NAME="topic-01"

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add kafka-ui https://provectus.github.io/kafka-ui-charts


# # Check if the service already exists
# if kubectl get svc -n $NAMESPACE | grep -q $KAFKA_DEPLOYMENT_NAME; then
#     echo "Service '$KAFKA_DEPLOYMENT_NAME' is already running."
# else
    echo "Service '$KAFKA_DEPLOYMENT_NAME' is not running. Deploying..."
    helm install $KAFKA_DEPLOYMENT_NAME bitnami/kafka --version 22.0.1 --set topics[0].name=topic-1,topics[0].partitions=1,topics[0].replicationFactor=2,externalAccess.enabled=true,externalAccess.service.type=NodePort,externalAccess.service.nodePorts[0]=30001 -n $NAMESPACE

# fi
 