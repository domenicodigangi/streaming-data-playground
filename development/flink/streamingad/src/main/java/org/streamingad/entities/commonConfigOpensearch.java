package org.streamingad.entities;

import org.apache.flink.api.java.utils.ParameterTool;

import java.io.IOException;

public class commonConfigOpensearch {
    static String propertiesFilePath = "src/main/resources/opensearch-config.properties";
    static ParameterTool parameters;

    static {
        try {
            parameters = ParameterTool.fromPropertiesFile(propertiesFilePath);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }


    public static final String HOST = parameters.get("host", "localhost");
    public static final Integer PORT = Integer.parseInt(parameters.get("port", "8080"));
    public static final String SCHEME = parameters.get("scheme", "http");
    public static final String USER = parameters.get("user", "admin");
    public static final String PASSWORD = parameters.get("password", "admin");
    public static final String VALUES_INDEX_NAME = parameters.get("valuesIndexName", "");
    public static final String ANOMALIES_INDEX_NAME = parameters.get("anomaliesIndexName", "");

    public commonConfigOpensearch() throws IOException {
    }

    // Example of usage
    public static void main(String[] args) {
        System.out.println("Host: " + HOST);
        System.out.println("Port: " + PORT);
        System.out.println("Scheme: " + SCHEME);
        System.out.println("Values Index Name: " + VALUES_INDEX_NAME);
        System.out.println("Anomalies Index Name: " + ANOMALIES_INDEX_NAME);

    }
}
