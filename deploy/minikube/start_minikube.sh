#!/bin/bash
NAMESPACE="default"

# Check if Minikube is running
if minikube status | grep -q "host: Running"; then
    echo "Minikube is already running."
else
    echo "Minikube is not running. Starting Minikube..."
    minikube start --cpus=3 --memory=10GB --disk-size=10GB   > minikube.log 2>&1
fi
 