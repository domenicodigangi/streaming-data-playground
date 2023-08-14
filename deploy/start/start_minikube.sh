#!/bin/bash
NAMESPACE="default"

# Check if Minikube is running
if minikube status | grep -q "host: Running"; then
    echo "Minikube is already running."
else
    echo "Minikube is not running. Starting Minikube..."
    nohup bash -c 'minikube start --cpus=4 --memory=10GB --disk-size=10 &' > minikube.log 2>&1
fi
 