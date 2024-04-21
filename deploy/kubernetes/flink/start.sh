helm repo add flink-kubernetes-operator-1.7.0 https://archive.apache.org/dist/flink/flink-kubernetes-operator-1.7.0/

helm search repo flink-kubernetes-operator-1.7.0

helm show values flink-kubernetes-operator-1.7.0/flink-kubernetes-operator

kubectl create ns flink-operator
kubectl create ns flink-jobs
helm -n flink-operator install -f /workspaces/streaming-anomaly-detection/deploy/kubernetes/flink/values.yml flink-kubernetes-operator flink-kubernetes-operator-1.7.0/flink-kubernetes-operator --set webhook.create=false