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

## To ssh into codespace (useful for remote development wih pycharm)
Example for windows
```PowerShell
Host cs.special-waddle-4prvjrp54v27wxg.main
        User vscode
        ProxyCommand C:\Program Files\GitHub CLI\gh.exe cs ssh -c special-waddle-4prvjrp54v27wxg --stdio -- -i C:\Users\<username>\.ssh\codespaces.jetbrains
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking no
        LogLevel quiet
        ControlMaster auto
        IdentityFile C:\Users\<username>\.ssh\codespaces.jetbrains
