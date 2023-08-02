helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka  bitnami/kafka --version 22.0.1

 kubectl run kafka-client-producer --restart='Never' --image docker.io/bitnami/kafka:3.4.0-debian-11-r22 --namespace default --command -- sleep infinity