#!/bin/bash
NAMESPACE="default"

# Get available CPUs and Memory in the system
available_cpus=$(nproc)
available_memory=$(awk '/MemAvailable/ {printf "%.f", $2/1024/1024}' /proc/meminfo) # in GB

# Subtract 2GB from available memory
available_memory=$((available_memory - 1))

# Set maximum limit for Minikube resources
max_cpus=3
max_memory=10 # in GB

# Choose the smaller between the available and maximum resources
final_cpus=$(( available_cpus < max_cpus ? available_cpus : max_cpus ))
final_memory=$(( available_memory < max_memory ? available_memory : max_memory ))

# Log the resources being used
echo "Available CPUs: $available_cpus"
echo "Available Memory: ${available_memory}GB (1GB subtracted)"
echo "Allocating CPUs for Minikube: $final_cpus"
echo "Allocating Memory for Minikube: ${final_memory}GB"

# Check if Minikube is running
if minikube status | grep -q "host: Running"; then
    echo "Minikube is already running."
else
    echo "Minikube is not running. Starting Minikube..."
    minikube start --cpus=$final_cpus --memory="${final_memory}GB" --disk-size=10GB > minikube.log 2>&1
fi
