#!/bin/bash
NAMESPACE="default"

# Check if Minikube is running
if minikube status | grep -q "host: Running"; then
    echo "Minikube is already running."
else
    echo "Minikube is not running. Starting Minikube..."
    minikube start
fi

. deploy/kafka/kafka-deploy.sh

. deploy/grafana/grafana-deploy-and-forward-ports.sh
# run in grafana container
# grafana cli plugins install hamedkarbasi93-kafka-datasource

kubectl apply -f deploy/kafka-client-producer.yml 



