package org.streamingad.entities;

import org.apache.flink.api.java.utils.ParameterTool;

import java.io.IOException;

public class commonConfigKafka {
    static String propertiesFilePath = "src/main/resources/kafka-config.properties";
    static ParameterTool parameters;

    static {
        try {
            parameters = ParameterTool.fromPropertiesFile(propertiesFilePath);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    // Read from environment variables, fallback to properties file or default values
    public static final String BROKER = System.getenv("KAFKA_BROKER") != null ? System.getenv("KAFKA_BROKER") : parameters.get("broker", "kafka.hland.domotz.dev:31472");
    public static final String TOPIC_INPUT_DATA = System.getenv("KAFKA_TOPIC_INPUT_DATA") != null ? System.getenv("KAFKA_TOPIC_INPUT_DATA") : parameters.get("inputStreamName", "device-metrics");
    public static final String TOPIC_OUTPUT_DATA = System.getenv("KAFKA_TOPIC_OUTPUT_DATA") != null ? System.getenv("KAFKA_TOPIC_OUTPUT_DATA") : parameters.get("outputStreamName", "device-anomalies");

    public commonConfigKafka() throws IOException {
    }

    // Example of usage
    public static void main(String[] args) {
        System.out.println("Host: " + BROKER);
        System.out.println("Topic input data: " + TOPIC_INPUT_DATA);
        System.out.println("Topic output data: " + TOPIC_OUTPUT_DATA);
    }
}
