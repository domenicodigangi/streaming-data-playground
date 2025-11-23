# Real-Time Anomaly Detection on Streaming Data

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Java](https://img.shields.io/badge/Java-8%2B-orange.svg)](https://www.oracle.com/java/technologies/downloads/)

A production-ready demonstration platform showcasing **real-time anomaly detection** on streaming data using modern distributed systems architecture. This project combines **Apache Kafka**, **Apache Flink**, and **Amazon's Random Cut Forest algorithm** to detect anomalies in streaming time series data with interactive visualization.

## 🎯 Project Overview

This system demonstrates an end-to-end streaming data pipeline with real-time anomaly detection capabilities. It's designed as a portfolio project showcasing expertise in:

- **Stream Processing**: Apache Flink with custom operators
- **Message Streaming**: Apache Kafka for distributed messaging
- **Machine Learning**: Random Cut Forest algorithm for unsupervised anomaly detection
- **Visualization**: Interactive Streamlit dashboard with real-time updates
- **DevOps**: Docker Compose and Kubernetes deployment configurations

### Key Features

✨ **Real-time anomaly detection** using Random Cut Forest algorithm
📊 **Interactive dashboard** with live streaming charts and historical data viewing
🔧 **Configurable data simulator** with Gaussian distributions and anomaly injection
🚀 **Production-ready** with Docker Compose and Kubernetes deployments
📈 **Scalable architecture** supporting multiple concurrent data streams
🧪 **Comprehensive testing** with unit and integration tests
💾 **Redis caching** for efficient data persistence between UI refreshes

## 🏗️ Architecture

![Architecture Diagram](./images/streaming%20anomaly%20detection%20diagram.jpg)

### System Components

```
┌─────────────────┐
│ Data Simulator  │  FastAPI service generating Gaussian-distributed data
│   (Python)      │  - Configurable mean, variance, message rate
└────────┬────────┘  - Anomaly injection API
         │ publishes
         ↓
┌─────────────────┐
│     Kafka       │  Message broker
│   (Confluent)   │  - Topic: streamingad_simulated_data (input)
└────────┬────────┘  - Topic: streamingad_output (anomaly scores)
         │ consumes
         ↓
┌─────────────────┐
│  Apache Flink   │  Stream processor with Random Cut Forest
│     (Java)      │  - Custom RandomCutForestOperator
└────────┬────────┘  - Keyed state per data source
         │ publishes
         ↓
┌─────────────────┐
│     Kafka       │  (anomaly scores)
└────────┬────────┘
         │ consumes
         ↓
┌─────────────────┐
│   Streamlit     │  Web-based visualization dashboard
│   Dashboard     │  - Real-time charts (Plotly/Altair)
└─────────────────┘  - Redis caching for performance
```

### Data Flow

1. **Simulation**: Data simulator generates time series data following configurable Gaussian distributions
2. **Ingestion**: Data published to Kafka topic `streamingad_simulated_data`
3. **Processing**: Flink job consumes data, applies Random Cut Forest algorithm, calculates anomaly scores
4. **Output**: Enriched messages (with `score_ad` field) published to `streamingad_output` topic
5. **Visualization**: Streamlit dashboard subscribes to both topics, displays live charts with anomaly scores

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (for local deployment)
- **Maven 3.6+** and **Java 8+** (for building Flink job manually)
- **Python 3.11+** (for local development)
- **Kubernetes** and **Helm** (for production deployment - optional)

### Local Deployment with Docker Compose

The easiest way to run the entire system locally:

```bash
# Clone the repository
git clone https://github.com/domenicodigangi/streaming-data-playground.git
cd streaming-data-playground/components/streaming_anomaly_detection

# Start all services (builds Flink JAR automatically)
docker-compose up --build

# Wait for all services to start (~2-3 minutes)
# The Flink job will automatically be submitted after services are ready
```

**Access the services:**

- 🎨 **Streamlit Dashboard**: http://localhost:8501
- 🔧 **Flink Web UI**: http://localhost:8081
- 📡 **Data Simulator API**: http://localhost:8001/docs (FastAPI Swagger UI)
- 📨 **Kafka**: localhost:29092 (external), broker:9092 (internal)

### Manual Build (Alternative)

If you prefer to build components individually:

```bash
# Build Flink JAR
cd flink
./build.sh  # Requires Maven
cd ..

# Start services
docker-compose up
```

## 📖 Usage Guide

### Starting Data Generation

The data simulator automatically starts when the container launches. You can control it via:

1. **Streamlit UI** - Use the sidebar controls to adjust parameters
2. **API** - Direct HTTP calls to the simulator

#### Via Streamlit UI

Navigate to http://localhost:8501 and use the sidebar:

- **Mean**: Adjust the mean of the Gaussian distribution (0-10)
- **Variance**: Adjust the variance (0-10)
- **Messages/sec**: Control data generation rate (1-100)

#### Via API (cURL examples)

```bash
# Start a new data stream
curl -X POST "http://localhost:8001/gaussian_sampler/start/sensor_1" \
  -H "Content-Type: application/json" \
  -d '{"mean": 5.0, "variance": 2.0, "interval_sec": 0.5}'

# Update parameters for running stream
curl -X POST "http://localhost:8001/gaussian_sampler/sensor_1/update" \
  -H "Content-Type: application/json" \
  -d '{"mean": 7.0, "variance": 1.5}'

# Inject an anomaly (20 values, scaled to 100 observations)
curl -X POST "http://localhost:8001/gaussian_sampler/sensor_1/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [10.0, 12.0, 15.0, 18.0, 20.0, 22.0, 20.0, 18.0, 15.0, 12.0,
                10.0, 8.0, 6.0, 4.0, 3.0, 2.0, 1.0, 0.5, 0.2, 0.0],
    "n_observations": 100
  }'

# Stop data stream
curl -X POST "http://localhost:8001/gaussian_sampler/sensor_1/stop"
```

### Using the Dashboard

#### Real-Time Monitoring

- **Toggle "Live data"** to enable/disable real-time chart updates
- Charts update every few seconds with latest data
- Anomaly scores are overlaid on the data chart

#### Historical Data

- Use the **"Minutes to display"** slider to control the time window (1-60 minutes)
- Use the **"Historical messages to fetch"** slider for initial data load (1K-10K messages)
- Click **"Reset cache"** to clear all cached data and start fresh

#### Data Table View

- Toggle **"Show streaming data table"** to see raw message data
- Table displays: source_id, timestamp, value, and anomaly score

## 🔧 Configuration

### Data Simulator Configuration

Edit `data-simulator/conf/config_for_compose.yaml`:

```yaml
kafka:
  broker: "broker:9092"
  topic: "streamingad_simulated_data"

simulator:
  default_mean: 5.0
  default_variance: 2.0
  default_interval_sec: 0.5
```

### Flink Configuration

Edit `flink/streamingad/src/main/resources/kafka-config-for-compose.properties`:

```properties
broker=broker:9092
inputStreamName=streamingad_simulated_data
outputStreamName=streamingad_output
```

### Random Cut Forest Parameters

Edit `flink/streamingad/src/main/java/org/streamingad/operators/RandomCutForestOperator.java`:

```java
private static final int DIMENSIONS = 1;        // Univariate time series
private static final int SHINGLE_SIZE = 10;     // Sliding window size
private static final int SAMPLE_SIZE = 628;     // RCF sample size
```

## 🧪 Testing

The project includes comprehensive unit and integration tests.

### Running Tests

```bash
cd data-simulator

# Install test dependencies
poetry install --with dev

# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=simulator --cov-report=html --cov-report=term

# Run specific test file
poetry run pytest tests/test_anomaly_helper.py -v
```

See [data-simulator/tests/README.md](data-simulator/tests/README.md) for more details.

## 📚 API Documentation

Full API documentation is available at:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed endpoint descriptions and examples.

## 🚢 Kubernetes Deployment

For production deployment on Kubernetes:

```bash
cd kube-deploy/kubernetes

# Start local Minikube cluster (for testing)
./0_start_minikube.sh

# Deploy Kafka cluster
./kafka/start-kafka-cluster-and-ui.sh

# Deploy Flink with job
./flink/start.sh
```

**Note**: Kubernetes scripts contain environment-specific paths and configurations. Review and adjust before deploying to your cluster.

See [kube-deploy/README.md](../kube-deploy/README.md) for more details.

## 🐛 Troubleshooting

### Flink Job Not Running

**Symptoms**: No anomaly scores in Streamlit, Flink UI shows no running jobs

**Solutions**:
1. Check Flink JobManager logs: `docker-compose logs jobmanager`
2. Verify JAR was built: Check Flink UI at http://localhost:8081
3. Check Kafka connectivity: `docker-compose logs flink-job-submitter`
4. Manually submit job: `docker exec -it jobmanager flink run -d -c org.streamingad.StreamingADJob /opt/flink/usrlib/job.jar`

### No Data in Dashboard

**Symptoms**: Empty charts in Streamlit

**Solutions**:
1. Verify data simulator is running: Check http://localhost:8001/docs
2. Check Kafka messages:
   ```bash
   docker exec -it broker kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic streamingad_simulated_data --from-beginning
   ```
3. Check Streamlit logs: `docker-compose logs gui-streamlit`
4. Reset Redis cache: Click "Reset cache" in UI

### Maven Build Failures

**Symptoms**: `docker-compose build` fails with Maven errors

**Solutions**:
1. Check network connectivity to Maven Central
2. Clear Maven cache: `rm -rf ~/.m2/repository`
3. Try offline build if dependencies are cached: `mvn -o package`
4. Use manual build script: `cd flink && ./build.sh`

### Kafka Connection Refused

**Symptoms**: Simulator or Flink can't connect to Kafka

**Solutions**:
1. Ensure Kafka is fully started: `docker-compose logs broker`
2. Check network configuration in docker-compose.yml
3. Verify broker address in config files (should be `broker:9092` for internal)
4. Wait longer - Kafka can take 1-2 minutes to fully start

## 🔨 Development

### Project Structure

```
streaming_anomaly_detection/
├── data-simulator/          # Python FastAPI data generator
│   ├── src/simulator/
│   │   ├── core/           # Samplers and generators
│   │   └── app/            # FastAPI routes
│   ├── tests/              # Unit and integration tests
│   └── conf/               # Configuration files
├── flink/                  # Apache Flink stream processor
│   ├── streamingad/
│   │   └── src/main/java/org/streamingad/
│   │       ├── operators/  # Custom Flink operators (RCF)
│   │       └── jobs/       # Flink job definitions
│   ├── Dockerfile          # Multi-stage build
│   └── build.sh           # Build script
├── gui/streamlit_streaming_ad/  # Streamlit dashboard
│   ├── app.py             # Main dashboard
│   └── .streamlit/        # Configuration and secrets
├── docker-compose.yml     # Local deployment
└── kube-deploy/          # Kubernetes manifests

```

### Adding New Features

#### New Data Generator

1. Extend `AbstractSampler` in `data-simulator/src/simulator/core/data_generators/`
2. Implement `_sample_one_value()` method
3. Create corresponding router in `app/routers/`
4. Add tests in `tests/`

#### New Flink Operator

1. Create operator class extending `AbstractStreamOperator`
2. Implement `processElement()` method
3. Register in `StreamingADJob.java`
4. Rebuild Flink JAR

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Amazon Random Cut Forest**: Anomaly detection algorithm
- **Apache Flink**: Stream processing framework
- **Apache Kafka**: Distributed streaming platform
- **Streamlit**: Interactive dashboard framework

## 📧 Contact

Domenico Di Gangi - digangidomenico@gmail.com

Project Link: [https://github.com/domenicodigangi/streaming-data-playground](https://github.com/domenicodigangi/streaming-data-playground)

---

**Note**: This is a demonstration project designed for portfolio and educational purposes. For production use, additional hardening, monitoring, and security measures should be implemented.