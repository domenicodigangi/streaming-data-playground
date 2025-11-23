# Quick Start Guide

Get the Real-Time Anomaly Detection system up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports available: 8501, 8081, 8001, 29092, 2181

## Step 1: Clone and Navigate

```bash
git clone https://github.com/domenicodigangi/streaming-data-playground.git
cd streaming-data-playground/components/streaming_anomaly_detection
```

## Step 2: Start the System

```bash
# Start all services (this will take 2-3 minutes on first run)
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

**What's happening:**
- 🔵 Zookeeper and Kafka start
- 🔵 Data Simulator builds and starts generating data
- 🔵 Flink builds the JAR and starts JobManager/TaskManager
- 🔵 Flink job is automatically submitted
- 🔵 Streamlit dashboard starts

## Step 3: Verify Services are Running

Wait for log messages indicating services are ready:

```bash
# Check service health
docker-compose ps

# Expected output:
# NAME                    STATUS
# broker                  Up
# zookeeper               Up
# data-simulator          Up
# gui-streamlit           Up
# jobmanager              Up
# taskmanager             Up
# flink-job-submitter     Exited (0)  # This should exit after submitting job
```

## Step 4: Access the Dashboard

Open your browser and navigate to:

### 🎨 Main Dashboard
**http://localhost:8501**

You should see:
- Real-time streaming data chart
- Anomaly score overlay
- Simulator control panel in sidebar

### 🔧 Flink Web UI
**http://localhost:8081**

- View running jobs
- Check task managers
- Monitor job metrics

### 📡 Data Simulator API
**http://localhost:8001/docs**

- Interactive API documentation
- Test endpoints directly

## Step 5: Generate Your First Anomaly!

### Option A: Via Dashboard (Easiest)

1. In the Streamlit dashboard sidebar, adjust parameters:
   - Set **Mean** to 5.0
   - Set **Variance** to 1.0
   - Set **Messages/sec** to 10

2. Watch the chart for 30 seconds to establish baseline

3. Inject an anomaly using the API:

```bash
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [0, 0, 5, 10, 15, 20, 25, 20, 15, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "n_observations": 100
  }'
```

4. Watch the anomaly appear in the dashboard with elevated anomaly scores!

### Option B: Via API (More Control)

```bash
# 1. Start a new data stream with specific parameters
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/demo" \
  -H "Content-Type: application/json" \
  -d '{
    "mean": 5.0,
    "variance": 1.0,
    "interval_sec": 0.1
  }'

# 2. Wait 30 seconds for baseline
sleep 30

# 3. Inject spike anomaly
curl -X POST "http://localhost:8001/v1/gaussian/demo/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [0, 0, 10, 20, 30, 40, 30, 20, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "n_observations": 50
  }'

# 4. Wait to observe anomaly
sleep 30

# 5. Inject gradual drift
curl -X POST "http://localhost:8001/v1/gaussian/demo/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    "n_observations": 100
  }'
```

## Step 6: Explore the System

### Monitor Flink Job

Visit **http://localhost:8081** to:
- See the job DAG (Directed Acyclic Graph)
- Check throughput metrics
- View task manager statistics

### Check Kafka Messages

```bash
# View raw input messages
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic streamingad_simulated_data \
  --max-messages 10

# View anomaly scores
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic streamingad_output \
  --max-messages 10
```

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f data-simulator
docker-compose logs -f jobmanager
docker-compose logs -f gui-streamlit
```

## Step 7: Experiment!

Try these experiments:

### A. Vary Data Distribution
```bash
# High variance (noisy data)
curl -X POST "http://localhost:8001/v1/gaussian/demo/update" \
  -d '{"variance": 5.0}'

# Low variance (stable data)
curl -X POST "http://localhost:8001/v1/gaussian/demo/update" \
  -d '{"variance": 0.1}'

# Different mean
curl -X POST "http://localhost:8001/v1/gaussian/demo/update" \
  -d '{"mean": 15.0}'
```

### B. Test Different Anomaly Patterns

**Sudden Spike:**
```bash
curl -X POST "http://localhost:8001/v1/gaussian/demo/anomaly" \
  -d '{"values": [0,0,0,0,50,50,50,0,0,0,0,0,0,0,0,0,0,0,0,0], "n_observations": 40}'
```

**Gradual Increase:**
```bash
curl -X POST "http://localhost:8001/v1/gaussian/demo/anomaly" \
  -d '{"values": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], "n_observations": 100}'
```

**Sinusoidal Pattern:**
```bash
curl -X POST "http://localhost:8001/v1/gaussian/demo/anomaly" \
  -d '{"values": [0,5.9,9.5,9.5,5.9,0,-5.9,-9.5,-9.5,-5.9,0,5.9,9.5,9.5,5.9,0,-5.9,-9.5,-9.5,-5.9], "n_observations": 200}'
```

### C. Multiple Data Sources

Run multiple samplers concurrently:

```bash
# Start sensor 1
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/sensor_1" \
  -d '{"mean": 5.0, "variance": 1.0}'

# Start sensor 2
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/sensor_2" \
  -d '{"mean": 10.0, "variance": 2.0}'

# Start sensor 3
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/sensor_3" \
  -d '{"mean": 7.5, "variance": 1.5}'
```

Each sensor will have its own independent anomaly detection model!

## Stopping the System

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Troubleshooting

### Dashboard Shows No Data

**Solution:**
```bash
# 1. Check if simulator is running
docker-compose logs data-simulator

# 2. Verify Kafka has messages
docker exec -it broker kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic streamingad_simulated_data \
  --max-messages 5

# 3. Restart dashboard
docker-compose restart gui-streamlit
```

### Flink Job Not Running

**Solution:**
```bash
# 1. Check Flink logs
docker-compose logs jobmanager
docker-compose logs flink-job-submitter

# 2. Verify job in Flink UI
# Open http://localhost:8081

# 3. Manually submit job if needed
docker exec -it jobmanager flink run -d \
  -c org.streamingad.StreamingADJob \
  /opt/flink/usrlib/job.jar
```

### Port Already in Use

**Solution:**
```bash
# Find process using port (example: 8501)
lsof -i :8501

# Kill the process or change port in docker-compose.yml
```

## Next Steps

- 📖 Read the [full README](README.md) for detailed documentation
- 🔌 Check the [API Documentation](API_DOCUMENTATION.md) for all endpoints
- 🏗️ Review [Architectural Decisions](DECISIONS.md) to understand design choices
- 🧪 Run tests: `cd data-simulator && poetry run pytest`
- ☸️ Deploy to Kubernetes: `cd kube-deploy/kubernetes && ./start_all.sh`

## Demo Script

Want to show this to someone? Run this complete demo:

```bash
# Complete 2-minute demo
cd streaming-data-playground/components/streaming_anomaly_detection

# 1. Start system (wait 2-3 min)
docker-compose up -d

# 2. Open dashboard
open http://localhost:8501  # macOS
# or: xdg-open http://localhost:8501  # Linux

# 3. Wait 30 seconds for baseline

# 4. Inject dramatic spike anomaly
curl -X POST "http://localhost:8001/v1/gaussian/gaussian_sampler/start/anomaly" \
  -d '{"values": [0,0,0,0,50,100,50,0,0,0,0,0,0,0,0,0,0,0,0,0], "n_observations": 50}'

# 5. Point to the red spike in anomaly score! 🎉

# 6. Clean up
docker-compose down -v
```

---

**Having issues?** Check the [Troubleshooting section](README.md#-troubleshooting) in the main README or open an issue on GitHub.

**Enjoying the project?** ⭐ Star the repository!
