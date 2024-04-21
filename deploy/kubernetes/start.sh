. start_minikube.sh
minikube addons enable ingress

kubectl create namespace minio-dev

kubectl apply -f minio/

. flink/start.sh