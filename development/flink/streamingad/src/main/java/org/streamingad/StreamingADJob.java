/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.streamingad;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.opensearch.sink.OpensearchSinkBuilder;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.type.TypeFactory;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.http.HttpHost;
import org.opensearch.action.index.IndexRequest;
import org.opensearch.client.Requests;
import org.streamingad.entities.InputData;
import org.streamingad.entities.OutputData;
import org.streamingad.entities.commonConfigKafka;
import org.streamingad.entities.commonConfigOpensearch;
import org.streamingad.operator.RandomCutForestOperator;

import java.util.HashMap;
import java.util.Map;

public class StreamingADJob {
    static ObjectMapper mapper = new ObjectMapper();

    private static DataStream<InputData> createSource(
            final StreamExecutionEnvironment env) {

        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
                .setBootstrapServers(commonConfigKafka.BROKER)
                .setTopics(commonConfigKafka.TOPIC_INPUT_DATA)
                .setStartingOffsets(OffsetsInitializer.latest())
                .setValueOnlyDeserializer(new SimpleStringSchema())
                .build();


        return env
                .fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), "Kafka Source")
                .map(InputData::new);

    }

    private static IndexRequest createIndexRequest(String element) {
        Map<String, Object> json = new HashMap<>();
        json.put("data", element);

        return Requests.indexRequest()
                .index(commonConfigOpensearch.VALUES_INDEX_NAME)
                .source(json);
    }

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();


        DataStream<InputData> inputStream = createSource(env);

        RandomCutForestOperator<InputData, OutputData> randomCutForestOperator =
                RandomCutForestOperator.<InputData, OutputData>builder()
                        .setDimensions(1)
                        .setShingleSize(1)
                        .setSampleSize(628)
                        .setInputDataMapper((inputData) -> new float[]{inputData.getValue()})
                        .setResultMapper(((inputData, score) -> new OutputData(inputData.getTimestamp(), inputData.getValue(), score)))
                        .build();

        inputStream.map(new MapFunction<InputData, String>() {
            @Override
            public String map(InputData value) throws Exception {
                factory = TypeFactory.defaultInstance();
                type = factory.constructMapType(HashMap.class, String.class, String.class);
                result = mapper.readValue(data, type);
                return mapper.writeValueAsString(value);
            }
        }).sinkTo(
                new OpensearchSinkBuilder<String>()
                        .setBulkFlushMaxActions(1) // Instructs the sink to emit after every element, otherwise they would be buffered
                        .setHosts(new HttpHost(commonConfigOpensearch.HOST, commonConfigOpensearch.PORT, commonConfigOpensearch.SCHEME))
                        .setConnectionUsername(commonConfigOpensearch.USER)
                        .setConnectionPassword(commonConfigOpensearch.PASSWORD)
                        .setEmitter(
                                (element, context, indexer) ->
                                        indexer.add(createIndexRequest(element)))
                        .build());


        inputStream.print();

        env.execute();
    }
}
