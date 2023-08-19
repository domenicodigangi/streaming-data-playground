#!/bin/bash

# Log the start of the script
echo "Starting deployment script..."

# Deploy the Strimzi Operator
echo "Deploying Strimzi Operator..."
. deploy/kafka/strimzi_operator_based/deploy_strimzi_operator.sh 

# Deploy Kafka
echo "Deploying Kafka..."
. deploy/kafka/strimzi_operator_based/deploy_kafka.sh 

# Deploy Kafka UI
echo "Deploying Kafka UI..."
. deploy/kafka/helm_based_ui/kafka-ui-deploy.sh 

# Deploy Grafana
echo "Deploying and forwarding Grafana ports..."
. deploy/grafana/grafana-deploy-and-forward-ports.sh

 
# Log the end of the script
echo "Deployment script completed."
