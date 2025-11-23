#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../" && pwd)"

# Update this path if your deployment YAML is in a different location
DEPLOYMENT_YAML="${SCRIPT_DIR}/deployment/streamingad.yml"

if [ -f "${DEPLOYMENT_YAML}" ]; then
    kubectl create -f "${DEPLOYMENT_YAML}"
else
    echo "Warning: Deployment file not found at ${DEPLOYMENT_YAML}"
    echo "Please specify the correct path to your Flink job deployment YAML"
    exit 1
fi