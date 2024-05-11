get-flink:
  ifne "$(wildcard /workspaces/.codespaces/shared/flink-1.18.1/flink-1.18.1-bin-scala_2.12.tgz)"
    @wget -P /workspaces/.codespaces/shared/flink-1.18.1 https://dlcdn.apache.org/flink/flink-1.18.1/flink-1.18.1-bin-scala_2.12.tgz
    @tar -xzf /workspaces/.codespaces/shared/flink-1.18.1/flink-1.18.1-bin-scala_2.12.tgz -C /workspaces/.codespaces/shared/flink-1.18.1
  end
