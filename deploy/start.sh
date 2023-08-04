# minikube start

## Grafana
kubectl apply -f deploy/grafana/grafana-deployment.yml 
# run in grafana container
# grafana cli plugins install hamedkarbasi93-kafka-datasource

kubectl apply -f deploy/kafka-client-producer.yml 



