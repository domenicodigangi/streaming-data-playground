#!/bin/bash

DEPLOYMENT="grafana-deployment"
# Apply the deployment
kubectl apply -f deploy/grafana/grafana-deployment.yml 

# Wait for the deployment to be ready
while [[ $(kubectl get pods -l app=grafana -n $NAMESPACE -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do echo "waiting for pod" && sleep 1; done

# Set up port forwarding
nohup kubectl port-forward -n $NAMESPACE deployment/$DEPLOYMENT 3000:3000 || true &

#todo add conf as code for kafka grafana conn
KAFKA_SERVER_PATH="kafka.default.svc.cluster.local:9092"



# Print a reminder for running commands in Grafana container
echo "To install the Kafka Datasource plugin in Grafana, run the following command in Grafana container:"
echo "grafana-cli plugins install hamedkarbasi93-kafka-datasource"
