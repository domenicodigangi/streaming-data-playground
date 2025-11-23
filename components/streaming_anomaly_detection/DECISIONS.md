# Architectural Decisions and Design Notes

This document records important architectural decisions and explains why certain features are implemented or disabled.

## Decision Record

### 1. OpenSearch Integration (Disabled by Default)

**Status**: Optional feature, commented out in production code

**Context**:
The project originally included OpenSearch sinks for:
- Storing raw input data
- Persisting anomaly scores for long-term analysis
- Enabling complex queries and visualization

**Decision**:
OpenSearch integration is commented out but preserved in the codebase.

**Rationale**:
1. **Simplified Deployment**: Adding OpenSearch requires additional infrastructure (ES cluster, configuration, monitoring)
2. **Portfolio Focus**: The core streaming pipeline (Kafka → Flink → Streamlit) demonstrates the key capabilities
3. **Resource Constraints**: OpenSearch adds significant memory/CPU overhead for local development
4. **Preserved for Production**: The code remains available for production deployments where persistence is needed

**Trade-offs**:
- ✅ Easier local deployment and demonstration
- ✅ Lower resource requirements
- ❌ No long-term persistence of raw data or anomaly scores
- ❌ Limited historical analysis capabilities beyond Kafka retention

**How to Enable**:
1. Deploy OpenSearch cluster
2. Configure `commonConfigOpensearch` in Flink job
3. Uncomment `sinkToOpensearch()` calls in `StreamingADJob.java`
4. Rebuild and redeploy Flink job

**Files Affected**:
- `flink/streamingad/src/main/java/org/streamingad/StreamingADJob.java` (lines 59, 86)
- `flink/streamingad/src/main/java/org/streamingad/entities/commonConfigOpensearch.java`

---

### 2. PostgreSQL Dumping Job (Not Implemented)

**Status**: Skeleton code exists, not functional

**Context**:
Initial plan included a separate Flink job (`KafkaToPostgresJob.java`) to dump streaming data to PostgreSQL for batch analytics.

**Decision**:
PostgreSQL job remains as reference code but is not active in the deployment.

**Rationale**:
1. **Redundant with OpenSearch**: Both solve similar persistence problems
2. **Limited Value**: For this demonstration, Kafka + Redis caching provides sufficient data access
3. **Complexity**: Would require additional database management, migrations, and queries

**Future Considerations**:
- PostgreSQL might be preferred for:
  - Transactional guarantees
  - Relational data models
  - Integration with existing SQL-based analytics

**Files Affected**:
- `flink/streamingad/src/main/java/org/streamingad/KafkaToPostgresJob.java`

---

### 3. Flink Deployment: Docker Compose vs Kubernetes

**Status**: Both supported, Docker Compose is primary

**Context**:
The project supports two deployment models:
1. **Docker Compose**: Complete local environment with Flink job auto-submission
2. **Kubernetes**: Production-like deployment with Flink operator

**Decision**:
Docker Compose is the recommended approach for demos and development.

**Rationale**:
1. **Ease of Use**: Single `docker-compose up` command starts everything
2. **Resource Efficiency**: No Kubernetes overhead for local development
3. **Quick Iteration**: Faster rebuild and restart cycles
4. **Portfolio Presentation**: Simpler for reviewers to run and evaluate

**Trade-offs**:
- Docker Compose:
  - ✅ Simple, fast, resource-efficient
  - ❌ Not production-grade
  - ❌ Limited scaling capabilities
- Kubernetes:
  - ✅ Production-ready
  - ✅ Scalable and resilient
  - ❌ Complex setup
  - ❌ Resource-intensive

**Files Affected**:
- `docker-compose.yml` - Local development
- `kube-deploy/kubernetes/` - Kubernetes manifests and scripts

---

### 4. Random Cut Forest Parameters

**Status**: Current configuration optimized for demonstration

**Context**:
Random Cut Forest has several tunable parameters:
- **Dimensions**: 1 (univariate time series)
- **Shingle Size**: 10 (window size)
- **Sample Size**: 628 (RCF tree sample size)

**Decision**:
These values are chosen for balance between detection quality and performance.

**Rationale**:
1. **Dimensions = 1**: Most time series anomaly detection is univariate
2. **Shingle Size = 10**: Captures short-term patterns (10 observations)
3. **Sample Size = 628**: Default from AWS RCF library, good for general use

**Tuning Guide**:
- Increase `shingleSize` for longer-term pattern detection (e.g., 50-100)
- Increase `sampleSize` for more accurate detection at cost of memory/CPU
- For multivariate data, increase `dimensions` and adjust input mapper

**Files Affected**:
- `flink/streamingad/src/main/java/org/streamingad/StreamingADJob.java:64-66`
- `flink/streamingad/src/main/java/org/streamingad/operator/RandomCutForestOperator.java`

---

### 5. Redis Caching in Streamlit

**Status**: Implemented and active

**Context**:
Streamlit reruns the entire script on every interaction, which would cause:
- Data loss between refreshes
- Redundant Kafka consumption
- Poor user experience

**Decision**:
Use Redislite (embedded Redis) for caching data between Streamlit refreshes.

**Rationale**:
1. **State Persistence**: Maintains data across Streamlit reruns
2. **Performance**: Avoids re-fetching historical data
3. **Simplicity**: Redislite requires no external server
4. **User Control**: "Reset cache" button for clearing data

**Trade-offs**:
- ✅ Smooth user experience
- ✅ No external dependencies (Redislite is embedded)
- ❌ Cache is per-container (not shared across instances)
- ❌ Cache cleared on container restart

**Files Affected**:
- `gui/streamlit_streaming_ad/app.py`

---

### 6. Testing Strategy

**Status**: Unit tests for simulator, limited integration tests

**Context**:
Testing distributed streaming systems is challenging due to:
- External dependencies (Kafka, Flink)
- Asynchronous message processing
- Stateful operations

**Decision**:
Focus on unit tests for core logic, integration tests where practical.

**Rationale**:
1. **Unit Tests**: Cover data generation, anomaly rescaling, sampling logic
2. **Integration Tests**: Test API endpoints and workflow without Kafka
3. **Manual Testing**: Full end-to-end pipeline tested via docker-compose

**Coverage**:
- ✅ Data simulator logic (100% core functionality)
- ✅ Anomaly rescaling algorithm
- ✅ Gaussian sampling and deltas
- ⚠️ Limited Flink operator testing (requires test Kafka)
- ❌ No end-to-end automated pipeline tests

**Files Affected**:
- `data-simulator/tests/`

---

### 7. Logging and Debugging

**Status**: INFO level logging, print statements for Flink output

**Context**:
Need visibility into system behavior for troubleshooting.

**Decision**:
- Python: Structured logging with `logging` module (INFO level)
- Java: SLF4J with Log4j (INFO level)
- Flink output: `.print()` to stdout for debugging

**Rationale**:
1. **Development Focus**: Verbose enough for debugging, not overwhelming
2. **Container Logs**: Easy access via `docker-compose logs`
3. **Flink Output**: Visible in JobManager logs and stdout

**Production Recommendations**:
- Set log level to WARN or ERROR
- Remove `.print()` statements from Flink jobs
- Use structured logging (JSON format)
- Ship logs to centralized system (ELK, Splunk)

**Files Affected**:
- `data-simulator/src/simulator/` - Python logging configuration
- `flink/streamingad/src/main/resources/log4j.properties` - Log4j config

---

### 8. Multi-Source Support

**Status**: Fully implemented via keyed streams

**Context**:
Real-world scenarios often involve multiple data sources requiring independent anomaly detection.

**Decision**:
Use `source_id` as Kafka key and Flink keyBy() for per-source state management.

**Rationale**:
1. **Isolation**: Each source has independent RCF model
2. **Scalability**: Flink distributes keyed streams across task slots
3. **Kafka Partitioning**: Keys enable predictable message routing

**Implementation**:
- Data simulator: `source_id = f"{sampler_type}_{sampler_id}"`
- Kafka: Messages keyed by `source_id`
- Flink: `keyBy(InputData::getSourceID)`
- RCF: Separate model per source_id (managed by keyed state)

**Files Affected**:
- `data-simulator/src/simulator/core/data_generators/abstract_sampler.py:29-30`
- `flink/streamingad/src/main/java/org/streamingad/StreamingADJob.java:76`

---

## Future Enhancements

### Potential Additions

1. **Alert System**: Add alerting based on anomaly score thresholds (e.g., SNS, email)
2. **Model Persistence**: Save/load RCF models for faster restarts
3. **Additional Algorithms**: Support for ARIMA, Prophet, or deep learning models
4. **Monitoring Dashboard**: Grafana dashboards for system metrics
5. **Data Quality Checks**: Validation, null handling, outlier filtering
6. **Backpressure Handling**: Better flow control for high-throughput scenarios

### Known Limitations

1. **No Authentication**: Kafka, Flink UI, APIs are unauthenticated
2. **Single Partition**: Kafka topics use single partition (limits throughput)
3. **No Disaster Recovery**: No backup/restore mechanisms
4. **Limited Error Recovery**: Basic retry logic, no dead letter queues
5. **Memory Constraints**: RCF models grow with unique source_ids

---

## Contributing

When making architectural changes:
1. Document the decision in this file
2. Explain the context and rationale
3. Note trade-offs and alternatives considered
4. Update affected code references
5. Add to Future Enhancements if applicable

---

**Last Updated**: 2025-11-23
**Maintainer**: Domenico Di Gangi
