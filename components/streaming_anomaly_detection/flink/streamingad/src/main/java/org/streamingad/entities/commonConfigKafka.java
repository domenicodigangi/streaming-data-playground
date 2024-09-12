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


    public static final String BROKER = parameters.get("broker", "localhost");
    public static final String TOPIC_INPUT_DATA = parameters.get("inputStreamName", "");
    public static final String TOPIC_OUTPUT_DATA = parameters.get("outputStreamName", "");

    public commonConfigKafka() throws IOException {
    }

    // Example of usage
    public static void main(String[] args) {
        System.out.println("Host: " + BROKER);
        System.out.println("Topic input data: " + TOPIC_INPUT_DATA);
        System.out.println("Topic output data: " + TOPIC_OUTPUT_DATA);
    }
}

