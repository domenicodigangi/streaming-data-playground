#!/bin/bash
INIT_DIR=$(pwd)
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"


# Deploy Kafka
echo "Deploying Kafka..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. ${SCRIPT_DIR}/strimzi_operator_based/deploy_kafka.sh 

# Deploy Kafka UI
echo "Deploying Kafka UI..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. ${SCRIPT_DIR}/helm_based_ui/kafka-ui-deploy.sh 

cd INIT_DIR