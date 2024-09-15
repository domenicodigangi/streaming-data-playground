//package org.kafkadump;
//
//import com.fasterxml.jackson.databind.JsonNode;
//import com.fasterxml.jackson.databind.ObjectMapper;
//import org.apache.flink.api.common.eventtime.WatermarkStrategy;
//import org.apache.flink.api.common.serialization.SimpleStringSchema;
//import org.apache.flink.api.common.typeinfo.Types;
//import org.apache.flink.api.java.tuple.Tuple2;
//import org.apache.flink.connector.kafka.source.KafkaSource;
//import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
//import org.apache.flink.streaming.api.datastream.DataStream;
//import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
//import org.apache.flink.types.Row;
//import org.streamingad.entities.commonConfigKafka;
//
//import java.util.HashMap;
//import java.util.Iterator;
//import java.util.Map;
//
//public class KafkaToPostgresJob {
//
//    public static void main(String[] args) throws Exception {
//        // Set up the streaming execution environment
//        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
//
//        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
//                .setBootstrapServers(commonConfigKafka.BROKER)
//                .setTopics(commonConfigKafka.TOPIC_INPUT_DATA)
//                .setStartingOffsets(OffsetsInitializer.latest())
//                .setValueOnlyDeserializer(new SimpleStringSchema())
//                .build();
//
//        // Create the Kafka data stream
//        DataStream<String> kafkaStream = env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "Kafka Source");
//
//        DataStream<Tuple2<Row, String>> rowStream = kafkaStream.flatMap((String jsonStr, Collector<Tuple2<Row, String>> out) -> {
//            ObjectMapper objectMapper = new ObjectMapper();
//            JsonNode jsonNode = objectMapper.readTree(jsonStr);
//
//            // Convert JSON to Row and extract schema information
//            Map<String, Object> fieldMap = new HashMap<>();
//            Iterator<Map.Entry<String, JsonNode>> fields = jsonNode.fields();
//            while (fields.hasNext()) {
//                Map.Entry<String, JsonNode> field = fields.next();
//                String key = field.getKey();
//                JsonNode value = field.getValue();
//
//                if (value.isInt()) {
//                    fieldMap.put(key, value.asInt());
//                } else if (value.isTextual()) {
//                    fieldMap.put(key, value.asText());
//                } else if (value.isDouble()) {
//                    fieldMap.put(key, value.asDouble());
//                } else if (value.isBoolean()) {
//                    fieldMap.put(key, value.asBoolean());
//                } // Add more types as needed
//            }
//
//            // Create a Row with dynamic arity
//            Row row = Row.withNames();
//            for (Map.Entry<String, Object> entry : fieldMap.entrySet()) {
//                row.setField(entry.getKey(), entry.getValue());
//            }
//
//            // Emit the Row and its corresponding schema (as JSON string for simplicity)
//            out.collect(new Tuple2<>(row, objectMapper.writeValueAsString(fieldMap.keySet())));
//        }).returns(Types.TUPLE(Types.GENERIC(Row.class), Types.STRING));
//
//        // Define PostgreSQL sink
//        SinkFunction<Tuple2<Row, String>> jdbcSink = JdbcSink.sink(
//                (Tuple2<Row, String> tuple, PreparedStatement ps) -> {
//                    Row row = tuple.f0;
//                    // Assuming the schema (column names) is passed in tuple.f1
//                    String[] columns = new ObjectMapper().readValue(tuple.f1, String[].class);
//
//                    for (int i = 0; i < columns.length; i++) {
//                        ps.setObject(i + 1, row.getField(columns[i]));
//                    }
//                },
//                (row) -> {
//                    // Dynamically construct the SQL query based on the schema
//                    String[] columns = new ObjectMapper().readValue(row.f1, String[].class);
//                    String placeholders = String.join(",", new String[columns.length]).replace("\0", "?");
//                    return "INSERT INTO my_table (" + String.join(",", columns) + ") VALUES (" + placeholders + ")";
//                },
//                JdbcExecutionOptions.builder()
//                        .withBatchSize(1000)
//                        .build(),
//                new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
//                        .withUrl("jdbc:postgresql://localhost:5432/mydb")
//                        .withDriverName("org.postgresql.Driver")
//                        .withUsername("username")
//                        .withPassword("password")
//                        .build()
//        );
//
//        // Sink the transformed data into PostgreSQL
//        rowStream.addSink(jdbcSink);
//        env.execute("Kafka to Postgres Job");
//    }
//}
