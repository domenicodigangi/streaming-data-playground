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

## To ssh into codespace from windows
```bash
Host cs.opulent-meme-4prvjrpvpv27p7x.main
        User root
        ProxyCommand C:\Program Files\GitHub CLI\gh.exe cs ssh -c opulent-meme-4prvjrpvpv27p7x --stdio -- -i C:\Users\<user-name>\.ssh\id_rsa
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking no
        LogLevel quiet
        ControlMaster auto
        IdentityFile C:\Users\<user-name>\.ssh\id_rsa