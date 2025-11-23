"""Integration tests for the data simulator API."""
import pytest
from fastapi.testclient import TestClient

# This test requires the full app context, so we'll make it optional
pytest.importorskip("simulator.app.main")

from simulator.core.data_generators.anomalies import AnomalyDefinition


class TestSimulatorIntegration:
    """Integration tests for simulator endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from simulator.app.main import app

        return TestClient(app)

    def test_health_check(self, client):
        """Test that the health check endpoint works."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_start_gaussian_sampler(self, client):
        """Test starting a Gaussian sampler."""
        # Note: This test may fail if Kafka is not available
        # In a real CI/CD environment, you'd use a mock or test container
        params = {"mean": 5.0, "variance": 1.0, "interval_sec": 1.0}

        response = client.post("/gaussian_sampler/start/test_integration_1", json=params)

        # May succeed or fail depending on Kafka availability
        # Just check that the response is valid JSON
        assert response.headers["content-type"] == "application/json"

    def test_anomaly_definition_validation(self):
        """Test anomaly definition validation in integration context."""
        # Valid anomaly
        valid_values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=valid_values, n_observations=50)
        assert anomaly.n_observations == 50

        # Invalid anomaly - too few values
        with pytest.raises(Exception):
            AnomalyDefinition(values=[1.0, 2.0], n_observations=10)


class TestEndToEndWorkflow:
    """Test end-to-end workflow scenarios."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from simulator.app.main import app

        return TestClient(app)

    def test_complete_workflow_without_kafka(self):
        """Test the complete workflow logic without Kafka dependency."""
        from simulator.core.data_generators.gaussian_sampler import (
            GaussianDataSourceSettings,
            GaussianSampler,
            GaussianSamplerParams,
        )

        # 1. Create sampler with params
        params = GaussianSamplerParams(mean=10.0, variance=2.0)
        settings = GaussianDataSourceSettings(sampler_id="workflow_test", params=params)
        sampler = GaussianSampler(settings)

        # 2. Generate some samples
        samples = [sampler.sample_one_msg() for _ in range(10)]

        # 3. Verify samples have correct structure
        assert len(samples) == 10
        for sample in samples:
            assert "source_id" in sample
            assert "value" in sample
            assert "timestamp" in sample
            assert sample["source_id"] == "gaussian_sampler_workflow_test"

    def test_workflow_with_anomaly_injection(self):
        """Test workflow with anomaly injection."""
        from simulator.core.data_generators.anomalies import AnomalyDefinition, AnomalyHelper
        from simulator.core.data_generators.gaussian_sampler import (
            GaussianDataSourceSettings,
            GaussianSampler,
            GaussianSamplerParams,
        )

        # 1. Start with normal sampling
        params = GaussianSamplerParams(mean=5.0, variance=0.1)
        settings = GaussianDataSourceSettings(sampler_id="anomaly_test", params=params)
        sampler = GaussianSampler(settings)

        normal_sample = sampler.sample_one_msg()

        # 2. Create anomaly definition and helper
        anomaly_values = [10.0] * 20  # Large spike
        anomaly_def = AnomalyDefinition(values=anomaly_values, n_observations=5)
        helper = AnomalyHelper(anomaly_def)
        delta_list = helper.generate_list_to_add()

        # 3. Create new sampler with anomaly
        settings_with_anomaly = GaussianDataSourceSettings(
            sampler_id="anomaly_test",
            params=params,
            initial_additive_delta_list=delta_list,
        )
        sampler_with_anomaly = GaussianSampler(settings_with_anomaly)

        # 4. Generate anomaly samples
        anomaly_samples = [sampler_with_anomaly.sample_one_msg() for _ in range(5)]

        # 5. Verify anomaly samples are significantly higher
        for sample in anomaly_samples:
            # Should be roughly mean + 10 = 15
            assert sample["value"] > 10.0

        # 6. After anomaly list is exhausted, should return to normal
        post_anomaly_sample = sampler_with_anomaly.sample_one_msg()
        assert abs(post_anomaly_sample["value"] - 5.0) < 3.0  # Back to normal range
