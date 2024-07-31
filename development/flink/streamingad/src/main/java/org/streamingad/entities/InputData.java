package org.streamingad.entities;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;

public class InputData {
    ObjectMapper mapper = new ObjectMapper();
    @JsonProperty("source_id")
    public String sourceId;

    @JsonProperty("timestamp")
    public long timestamp;

    @JsonProperty("value")
    public float value;

    public InputData() {
        // Default constructor needed for Jackson deserialization
    }

    public float getValue() {
        return value;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public InputData(String jsonSerialized) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            InputData deserialized = mapper.readValue(jsonSerialized, InputData.class);
            this.sourceId = deserialized.sourceId;
            this.timestamp = deserialized.timestamp;
            this.value = deserialized.value;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


}
