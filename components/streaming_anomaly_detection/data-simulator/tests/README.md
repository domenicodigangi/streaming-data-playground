# Data Simulator Tests

This directory contains unit and integration tests for the data simulator component.

## Test Structure

- `test_anomaly_helper.py` - Tests for anomaly rescaling functionality
- `test_gaussian_sampler.py` - Tests for Gaussian sampling logic
- `test_integration.py` - Integration tests for API endpoints and end-to-end workflows

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd /path/to/data-simulator
poetry install --with dev
```

Or with pip:

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests

```bash
# From data-simulator directory
poetry run pytest

# Or with pip
pytest
```

### Run with Coverage

```bash
poetry run pytest --cov=simulator --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test Files

```bash
poetry run pytest tests/test_anomaly_helper.py
poetry run pytest tests/test_gaussian_sampler.py
poetry run pytest tests/test_integration.py
```

### Run with Verbose Output

```bash
poetry run pytest -v
```

## Test Coverage

Current test coverage includes:

- ✅ Anomaly definition validation
- ✅ Anomaly rescaling (up/down scaling, edge cases)
- ✅ Gaussian sampler initialization and sampling
- ✅ Additive delta functionality
- ✅ Message structure validation
- ✅ End-to-end workflow without Kafka
- ✅ Anomaly injection workflow

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd components/streaming_anomaly_detection/data-simulator
    poetry install --with dev
    poetry run pytest --cov=simulator --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Notes

- Integration tests that require Kafka will be skipped if Kafka is not available
- Some tests use statistical validation (e.g., distribution checks) and may occasionally fail due to random variation
- Tests are configured to run automatically with pytest discovery
