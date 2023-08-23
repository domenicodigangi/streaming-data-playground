#!/bin/bash
INIT_DIR=$(pwd)
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"


# Deploy Kafka
echo "Deploying Kafka..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. ${SCRIPT_DIR}/deploy_kafka.sh 
cd $INIT_DIR

# Deploy Kafka UI
echo "Deploying Kafka UI..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. ${SCRIPT_DIR}/deploy-kafka-ui.sh 

cd $INIT_DIR