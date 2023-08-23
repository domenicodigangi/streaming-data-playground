#!/bin/bash
INIT_DIR=$(pwd)

# Log the start of the script
echo "Starting deployment script..."


echo "Reset minikube"
minikube delete
. deploy/minikube/start_minikube.sh
cd ${INIT_DIR}



# Deploy the Strimzi Operator
echo "Deploying All Kafka related resources..."
. deploy/kafka/start-cluster-and-ui.sh
cd ${INIT_DIR}

# Deploy Grafana
echo "Deploying and forwarding Grafana ports..."
. deploy/grafana/grafana-deploy-and-forward-ports.sh
cd ${INIT_DIR}

 
# Log the end of the script
echo "Deployment script completed."
