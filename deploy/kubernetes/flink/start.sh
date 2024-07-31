helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.8.0/

helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.8.0/
helm install flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator

# kubectl create ns flink-operator
# kubectl create ns flink-jobs

# helm -n flink-operator install -f /workspaces/streaming-anomaly-detection/deploy/kubernetes/flink/values.yml flink-kubernetes-operator flink-kubernetes-operator-1.8.0/flink-kubernetes-operator --set webhook.create=false