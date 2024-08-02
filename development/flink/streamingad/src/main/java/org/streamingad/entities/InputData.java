package org.streamingad.entities;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;

public class InputData {
    ObjectMapper mapper = new ObjectMapper();
    @JsonProperty("source_id")
    public String sourceId;

    @JsonProperty("timestamp")
    public long timestamp;

    @JsonProperty("value")
    public double value;

    public InputData() {
        // Default constructor needed for Jackson deserialization
    }

    public double getValue() {
        return value;
    }

    public String getSourceID() {
        return sourceId;
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

    public HashMap<String, ?> toHashMap() {
        HashMap<String, Object> map = new HashMap<>();
        map.put("source_id", this.sourceId);
        map.put("timestamp", this.timestamp);
        map.put("value", this.value);
        return map;
    }

}
