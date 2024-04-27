. /workspaces/streaming-anomaly-detection/deploy/kubernetes/start_minikube.sh

kubectl create -f https://github.com/jetstack/cert-manager/releases/download/v1.8.2/cert-manager.yaml

minikube addons enable ingress

kubectl create namespace minio-dev

kubectl apply -f minio/

. /workspaces/streaming-anomaly-detection/deploy/kubernetes/flink/start.sh