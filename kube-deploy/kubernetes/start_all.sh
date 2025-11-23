#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
. "${SCRIPT_DIR}/0_start_minikube.sh"

print_header "1_setup_minikube.sh"
. "${SCRIPT_DIR}/1_setup_minikube.sh"

print_header "start-kafka-cluster-and-ui.sh"
. "${SCRIPT_DIR}/kafka/start-kafka-cluster-and-ui.sh"

print_header "start_minio.sh"
. "${SCRIPT_DIR}/minio/start_minio.sh"

print_header "start_flink.sh"
. "${SCRIPT_DIR}/flink/start.sh"

