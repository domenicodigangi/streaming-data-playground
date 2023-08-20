#!/bin/bash

# Log the start of the script
echo "Starting deployment script..."

# Deploy the Strimzi Operator
echo "Deploying All Kafka related resources..."
. deploy/kafka/start-cluster-and-ui.sh


# Deploy Grafana
echo "Deploying and forwarding Grafana ports..."
. deploy/grafana/grafana-deploy-and-forward-ports.sh

 
# Log the end of the script
echo "Deployment script completed."
