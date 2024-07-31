#bash deploy/kafka/deploy_strimzi.sh

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Running in $SCRIPT_DIR"


# Apply the Strimzi installation YAML
kubectl apply -f "$SCRIPT_DIR/strimzy-operator-namespace-kafka.yml" -n kafka

# Watch the Kafka pods (this will continue until manually stopped)
timeout 5s  kubectl get pod -n kafka --watch

# Tail the logs of the Strimzi cluster operator for 5 seconds
timeout 2s kubectl logs deployment/strimzi-cluster-operator -n kafka -f
