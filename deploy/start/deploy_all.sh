 
. deploy/kafka/strimzi_operator_based/deploy_strimzi_operator.sh 
. deploy/kafka/strimzi_operator_based/deploy_kafka.sh 

. deploy/grafana/grafana-deploy-and-forward-ports.sh
# run in grafana container
# grafana cli plugins install hamedkarbasi93-kafka-datasource

# kubectl apply -f deploy/kafka/kafka-client-producer.yml 



