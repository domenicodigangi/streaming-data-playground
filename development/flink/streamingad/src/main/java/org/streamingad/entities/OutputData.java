package org.streamingad.entities;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;

public class OutputData {
    ObjectMapper mapper = new ObjectMapper();
    @JsonProperty("source_id")
    public String sourceId;

    @JsonProperty("timestamp")
    public long timestamp;

    @JsonProperty("value")
    public double value;

    @JsonProperty("score_ad")
    public double score_ad;

    public OutputData() {
        // Default constructor needed for Jackson deserialization
    }

    public OutputData(String sourceId, long timestamp, double value, double score_ad) {
        this.sourceId = sourceId;
        this.timestamp = timestamp;
        this.value = value;
        this.score_ad = score_ad;
    }

    public double getValue() {
        return value;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public OutputData(String jsonSerialized) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            OutputData deserialized = mapper.readValue(jsonSerialized, OutputData.class);
            this.sourceId = deserialized.sourceId;
            this.timestamp = deserialized.timestamp;
            this.value = deserialized.value;
            this.score_ad = deserialized.score_ad;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public HashMap<String, ?> toHashMap() {
        HashMap<String, Object> map = new HashMap<>();
        map.put("source_id", this.sourceId);
        map.put("timestamp", this.timestamp);
        map.put("value", this.value);
        map.put("score_ad", this.score_ad);
        return map;
    }

}
