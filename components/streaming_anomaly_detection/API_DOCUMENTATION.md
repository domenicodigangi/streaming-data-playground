# Data Simulator API Documentation

The Data Simulator provides a REST API for controlling data generation and anomaly injection. This document provides detailed information about all available endpoints.

## Base URL

```
http://localhost:8001
```

## Interactive Documentation

- **Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc**: [http://localhost:8001/redoc](http://localhost:8001/redoc)

## Endpoints

### Health Check

#### `GET /health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:8001/health
```

---

### Gaussian Sampler Endpoints

#### `POST /gaussian_sampler/start/{item_id}`

Start a new Gaussian data sampler.

**Path Parameters:**
- `item_id` (string): Unique identifier for this sampler (e.g., "sensor_1", "source_a")

**Request Body (optional):**
```json
{
  "mean": 5.0,          // Mean of Gaussian distribution (default: 0.1)
  "variance": 2.0,      // Variance of distribution (default: 1.0)
  "interval_sec": 0.5   // Seconds between samples (default: 0.5)
}
```

**Response:**
```json
{
  "status": "started",
  "task_name": "gaussian_sampler_sensor_1",
  "settings": {
    "sampler_id": "sensor_1",
    "source_id": "gaussian_sampler_sensor_1",
    "params": {
      "mean": 5.0,
      "variance": 2.0,
      "interval_sec": 0.5
    }
  }
}
```

**Example:**
```bash
# Start with default parameters
curl -X POST http://localhost:8001/gaussian_sampler/start/sensor_1

# Start with custom parameters
curl -X POST http://localhost:8001/gaussian_sampler/start/sensor_1 \
  -H "Content-Type: application/json" \
  -d '{
    "mean": 10.0,
    "variance": 3.0,
    "interval_sec": 1.0
  }'
```

---

#### `POST /gaussian_sampler/{item_id}/update`

Update parameters of a running Gaussian sampler.

**Path Parameters:**
- `item_id` (string): Identifier of the sampler to update

**Request Body (optional):**
```json
{
  "mean": 7.5,
  "variance": 1.5,
  "interval_sec": 0.25
}
```

**Response:**
```json
{
  "status": "updated",
  "task_name": "gaussian_sampler_sensor_1",
  "settings": {
    "sampler_id": "sensor_1",
    "params": {
      "mean": 7.5,
      "variance": 1.5,
      "interval_sec": 0.25
    }
  }
}
```

**Example:**
```bash
# Update mean and variance
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/update \
  -H "Content-Type: application/json" \
  -d '{
    "mean": 15.0,
    "variance": 5.0
  }'

# Update only message rate
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/update \
  -H "Content-Type: application/json" \
  -d '{
    "interval_sec": 0.1
  }'
```

---

#### `POST /gaussian_sampler/{item_id}/anomaly`

Inject an anomaly pattern into a running sampler.

**Path Parameters:**
- `item_id` (string): Identifier of the sampler

**Request Body:**
```json
{
  "values": [            // Exactly 20 float values
    10.0, 12.0, 15.0, 18.0, 20.0,
    22.0, 20.0, 18.0, 15.0, 12.0,
    10.0, 8.0, 6.0, 4.0, 3.0,
    2.0, 1.0, 0.5, 0.2, 0.0
  ],
  "n_observations": 100  // Number of samples to spread anomaly across
}
```

**Parameters:**
- `values`: Array of exactly 20 float values representing the anomaly pattern
- `n_observations`: Positive integer - total number of observations to apply the anomaly over

**How it works:**
1. The 20 input values are linearly interpolated to create `n_observations` values
2. These values are added to the next `n_observations` samples from the generator
3. After the anomaly is exhausted, the sampler returns to normal operation

**Response:**
```json
{
  "status": "anomaly_injected",
  "task_name": "gaussian_sampler_sensor_1",
  "anomaly_duration_samples": 100
}
```

**Example Anomaly Patterns:**

```bash
# Spike anomaly - sudden increase then decrease
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "values": [0, 0, 5, 10, 15, 20, 25, 20, 15, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "n_observations": 50
  }'

# Gradual increase
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "n_observations": 100
  }'

# Sinusoidal pattern
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "values": [0, 5.9, 9.5, 9.5, 5.9, 0, -5.9, -9.5, -9.5, -5.9, 0, 5.9, 9.5, 9.5, 5.9, 0, -5.9, -9.5, -9.5, -5.9],
    "n_observations": 200
  }'

# Constant offset (level shift)
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "values": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
    "n_observations": 150
  }'
```

---

#### `POST /gaussian_sampler/{item_id}/stop`

Stop a running Gaussian sampler.

**Path Parameters:**
- `item_id` (string): Identifier of the sampler to stop

**Response:**
```json
{
  "status": "stopped",
  "task_name": "gaussian_sampler_sensor_1"
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/stop
```

---

## Data Format

### Kafka Message Structure

Messages published to Kafka have the following JSON structure:

**Input Topic** (`streamingad_simulated_data`):
```json
{
  "source_id": "gaussian_sampler_sensor_1",
  "value": 5.234,
  "timestamp": 1700000000000
}
```

**Output Topic** (`streamingad_output` - after Flink processing):
```json
{
  "source_id": "gaussian_sampler_sensor_1",
  "value": 5.234,
  "timestamp": 1700000000000,
  "score_ad": 0.123
}
```

**Fields:**
- `source_id`: Unique identifier combining sampler type and ID
- `value`: The generated/sampled numeric value
- `timestamp`: Unix timestamp in milliseconds
- `score_ad`: Anomaly score from Random Cut Forest (0-1, higher = more anomalous)

---

## Error Responses

### 400 Bad Request

Invalid parameters provided.

```json
{
  "detail": "Validation error: values must contain exactly 20 elements"
}
```

### 404 Not Found

Sampler with specified ID not found.

```json
{
  "detail": "Task gaussian_sampler_sensor_1 not found"
}
```

### 500 Internal Server Error

Internal server error (e.g., Kafka connection failure).

```json
{
  "detail": "Failed to connect to Kafka broker"
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing rate limiting based on your requirements.

---

## Best Practices

### Sampler IDs

- Use descriptive, unique IDs: `sensor_1`, `device_a`, `source_production`
- Avoid special characters except underscore and hyphen
- Keep IDs short and meaningful

### Parameter Selection

**Mean and Variance:**
- For realistic data: mean=5-10, variance=1-3
- For stable data: variance=0.1-0.5
- For volatile data: variance=5-10

**Interval:**
- High-frequency: 0.01-0.1 seconds (10-100 msg/sec)
- Medium-frequency: 0.5-1.0 seconds (1-2 msg/sec)
- Low-frequency: 2-5 seconds

### Anomaly Injection

**Pattern Design:**
- Use smooth transitions for realistic anomalies
- Scale amplitude based on normal variance
- Consider anomaly duration vs. detection window

**Example workflow:**
```bash
# 1. Start normal sampling
curl -X POST http://localhost:8001/gaussian_sampler/start/test \
  -d '{"mean": 5.0, "variance": 1.0}'

# 2. Wait for baseline (30 seconds)
sleep 30

# 3. Inject spike anomaly
curl -X POST http://localhost:8001/gaussian_sampler/test/anomaly \
  -d '{"values": [0,0,5,10,15,20,15,10,5,0,0,0,0,0,0,0,0,0,0,0], "n_observations": 100}'

# 4. Wait for anomaly to complete
sleep 50

# 5. Inject gradual drift
curl -X POST http://localhost:8001/gaussian_sampler/test/anomaly \
  -d '{"values": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19], "n_observations": 200}'
```

---

## Python Client Example

```python
import requests
import time

BASE_URL = "http://localhost:8001"

class DataSimulatorClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def start_sampler(self, sampler_id, mean=5.0, variance=2.0, interval_sec=0.5):
        """Start a new Gaussian sampler."""
        url = f"{self.base_url}/gaussian_sampler/start/{sampler_id}"
        payload = {
            "mean": mean,
            "variance": variance,
            "interval_sec": interval_sec
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def update_sampler(self, sampler_id, **kwargs):
        """Update parameters of a running sampler."""
        url = f"{self.base_url}/gaussian_sampler/{sampler_id}/update"
        response = requests.post(url, json=kwargs)
        response.raise_for_status()
        return response.json()

    def inject_anomaly(self, sampler_id, values, n_observations):
        """Inject an anomaly pattern."""
        url = f"{self.base_url}/gaussian_sampler/{sampler_id}/anomaly"
        payload = {
            "values": values,
            "n_observations": n_observations
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def stop_sampler(self, sampler_id):
        """Stop a running sampler."""
        url = f"{self.base_url}/gaussian_sampler/{sampler_id}/stop"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    client = DataSimulatorClient()

    # Start sampler
    result = client.start_sampler("demo", mean=10.0, variance=2.0)
    print(f"Started: {result}")

    # Wait 30 seconds
    time.sleep(30)

    # Inject spike anomaly
    spike_values = [0] * 5 + [20, 25, 30, 25, 20] + [0] * 10
    result = client.inject_anomaly("demo", spike_values, 100)
    print(f"Anomaly injected: {result}")

    # Wait for anomaly to complete
    time.sleep(60)

    # Stop sampler
    result = client.stop_sampler("demo")
    print(f"Stopped: {result}")
```

---

## Troubleshooting

### "Failed to connect to Kafka"

**Solution:** Ensure Kafka broker is running and accessible at the configured address.

```bash
# Check Kafka is running
docker-compose logs broker

# Verify Kafka connectivity
docker exec -it broker kafka-topics --list --bootstrap-server localhost:9092
```

### "Task already exists"

**Solution:** Stop the existing task before starting a new one with the same ID.

```bash
curl -X POST http://localhost:8001/gaussian_sampler/sensor_1/stop
curl -X POST http://localhost:8001/gaussian_sampler/start/sensor_1
```

### "Validation error: values must contain exactly 20 elements"

**Solution:** Ensure your anomaly `values` array has exactly 20 elements.

```python
# Correct
values = [0.0] * 20

# Incorrect
values = [0.0] * 10  # Too few
```

---

For more information, see the [main README](README.md) or visit the interactive documentation at http://localhost:8001/docs.
