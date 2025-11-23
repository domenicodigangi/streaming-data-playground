#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add Flink operator Helm repo
helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.8.0/
helm repo update

# Install Flink Kubernetes operator
helm install flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator

# Optional: Create namespaces if needed
# kubectl create ns flink-operator
# kubectl create ns flink-jobs

# Optional: Install with custom values file
# VALUES_FILE="${SCRIPT_DIR}/values.yml"
# if [ -f "${VALUES_FILE}" ]; then
#     helm -n flink-operator install -f "${VALUES_FILE}" flink-kubernetes-operator \
#       flink-operator-repo/flink-kubernetes-operator --set webhook.create=false
# fi