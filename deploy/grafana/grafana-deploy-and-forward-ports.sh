#!/bin/bash

DEPLOYMENT="grafana-deployment"

# Apply the deployment
kubectl apply -f deploy/grafana/grafana-deployment.yml 

# Wait for the deployment to be ready
while [[ $(kubectl get pods -l app=grafana -n $NAMESPACE -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod" && sleep 1; done

# Set up port forwarding
nohup kubectl port-forward -n $NAMESPACE deployment/$DEPLOYMENT 3000:3000 || true &

