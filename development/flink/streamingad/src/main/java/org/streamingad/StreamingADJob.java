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
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.opensearch.sink.OpensearchSinkBuilder;
import org.apache.flink.formats.json.JsonSerializationSchema;
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

public class StreamingADJob {
    static ObjectMapper mapper = new ObjectMapper();


    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        DataStream<InputData> inputStream = streamFromKafkaSource(env);
//        sinkToOpensearch(inputStream.map(InputData::toHashMap), commonConfigOpensearch.VALUES_INDEX_NAME);

        RandomCutForestOperator<InputData, OutputData> randomCutForestOperator =
                RandomCutForestOperator.<InputData, OutputData>builder()
                        .setDimensions(1)
                        .setShingleSize(1)
                        .setSampleSize(628)
                        .setInputDataMapper((inputData) -> new double[]{inputData.getValue()})
                        .setResultMapper(((inputData, score) -> new OutputData(inputData.getSourceID(), inputData.getTimestamp(), inputData.getValue(), score)))
                        .build();

        DataStream<OutputData> outScoreStream = inputStream.process(randomCutForestOperator, TypeInformation.of(OutputData.class)).setParallelism(1);
        outScoreStream.map(OutputData::toHashMap).print();
//        sinkToOpensearch(outScoreStream.map(OutputData::toHashMap), commonConfigOpensearch.ANOMALIES_INDEX_NAME);


        outScoreStream.sinkTo(getKafkaSink());
        env.execute();
    }

    private static DataStream<InputData> streamFromKafkaSource(
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

    private static KafkaSink<OutputData> getKafkaSink() {
        JsonSerializationSchema<OutputData> jsonFormat = new JsonSerializationSchema<>();
        return KafkaSink.<OutputData>builder()
                .setBootstrapServers(commonConfigKafka.BROKER)
                .setRecordSerializer(KafkaRecordSerializationSchema.builder()
                        .setTopic(commonConfigKafka.TOPIC_OUTPUT_DATA)
                        .setValueSerializationSchema(jsonFormat)
                        .build()
                )
                .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();
    }


    private static void sinkToOpensearch(DataStream<HashMap<String, ?>> hashMapStream, String indexName) {
        hashMapStream.sinkTo(
                new OpensearchSinkBuilder<HashMap<String, ?>>()
                        .setBulkFlushMaxActions(1) // Instructs the sink to emit after every element, otherwise they would be buffered
                        .setHosts(new HttpHost(commonConfigOpensearch.HOST, commonConfigOpensearch.PORT, commonConfigOpensearch.SCHEME))
                        .setConnectionUsername(commonConfigOpensearch.USER)
                        .setConnectionPassword(commonConfigOpensearch.PASSWORD)
                        .setEmitter(
                                (element, context, indexer) ->
                                        indexer.add(createIndexRequest(element, indexName)))
                        .build());
    }

    private static IndexRequest createIndexRequest(HashMap<String, ?> element, String indexName) {
        return Requests.indexRequest()
                .index(indexName)
                .source(element);
    }
}
