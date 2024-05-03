#!/bin/bash

# Function to print header with filename and timestamp
print_header() {
    filename="$1"
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    echo 
    echo 
    echo "=========================================================="
    echo "Filename: $filename"
    echo "Timestamp: $timestamp"
    echo "=========================================================="
    echo 

}

print_header "0_start_minikube.sh"
. /workspaces/streaming-data-development-env/deploy/kubernetes/0_start_minikube.sh

print_header "1_setup_minikube.sh"
. /workspaces/streaming-data-development-env/deploy/kubernetes/1_setup_minikube.sh


print_header "start-kafka-cluster-and-ui.sh"
. /workspaces/streaming-data-development-env/deploy/kubernetes/kafka/start-kafka-cluster-and-ui.sh

print_header "start_minio.sh"
. /workspaces/streaming-data-development-env/deploy/kubernetes/minio/start_minio.sh

print_header "start_flink.sh"
. /workspaces/streaming-data-development-env/deploy/kubernetes/flink/start.sh


