# Streaming Data Infrastructure as Code (IAC)
## IAC for Local Development
Assuming that minikube and helm are installed run:
```bash
. deploy/kubernetes/start_all.sh

## Simulate a data stream
```bash
poetry install
poetry run simulator
```