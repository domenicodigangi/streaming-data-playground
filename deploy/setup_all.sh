## Kafka
helm repo add bitnami https://charts.bitnami.com/bitnami
minikube start
helm install kafka  bitnami/kafka --version 22.0.1
kubectl run kafka-client-producer --restart='Never' --image docker.io/bitnami/kafka:3.4.0-debian-11-r22 --namespace default --command -- sleep infinity

## Grafana
kubectl apply -f deployment/graphana-deployment.yml 
kubectl apply -f deployment/graphana-service.yml 
kubectl port-forward services/grafana-service 3000:3000 -n default
# run in grafana container
# grafana cli plugins install hamedkarbasi93-kafka-datasource
