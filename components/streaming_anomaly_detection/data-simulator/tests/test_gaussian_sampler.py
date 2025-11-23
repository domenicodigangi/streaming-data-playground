"""Unit tests for GaussianSampler."""
import pytest

from simulator.core.data_generators.gaussian_sampler import (
    GaussianDataSourceSettings,
    GaussianSampler,
    GaussianSamplerParams,
)


class TestGaussianSamplerParams:
    """Test GaussianSamplerParams model."""

    def test_default_params(self):
        """Test default parameter values."""
        params = GaussianSamplerParams()
        assert params.mean == 0.1
        assert params.variance == 1.0
        assert params.interval_sec == 0.5
        assert params.name == "gaussian_sampler"

    def test_custom_params(self):
        """Test setting custom parameters."""
        params = GaussianSamplerParams(mean=5.0, variance=2.0, interval_sec=1.0)
        assert params.mean == 5.0
        assert params.variance == 2.0
        assert params.interval_sec == 1.0


class TestGaussianSampler:
    """Test GaussianSampler functionality."""

    def test_sampler_initialization(self):
        """Test that sampler initializes correctly."""
        params = GaussianSamplerParams(mean=0.0, variance=1.0)
        settings = GaussianDataSourceSettings(sampler_id="test_1", params=params)
        sampler = GaussianSampler(settings)

        assert sampler.params.mean == 0.0
        assert sampler.params.variance == 1.0
        assert sampler.source_id == "gaussian_sampler_test_1"

    def test_sample_one_msg_structure(self):
        """Test that sample_one_msg returns correct structure."""
        params = GaussianSamplerParams(mean=5.0, variance=1.0)
        settings = GaussianDataSourceSettings(sampler_id="test_2", params=params)
        sampler = GaussianSampler(settings)

        msg = sampler.sample_one_msg()

        assert "source_id" in msg
        assert "value" in msg
        assert "timestamp" in msg
        assert msg["source_id"] == "gaussian_sampler_test_2"
        assert isinstance(msg["value"], float)
        assert isinstance(msg["timestamp"], int)
        assert msg["timestamp"] > 0

    def test_sample_multiple_values_distribution(self):
        """Test that multiple samples follow roughly Gaussian distribution."""
        params = GaussianSamplerParams(mean=10.0, variance=4.0)
        settings = GaussianDataSourceSettings(sampler_id="test_3", params=params)
        sampler = GaussianSampler(settings)

        # Generate many samples
        samples = [sampler.sample_one_msg()["value"] for _ in range(1000)]

        # Check that mean is roughly correct (within 1 standard deviation / sqrt(n))
        sample_mean = sum(samples) / len(samples)
        assert abs(sample_mean - 10.0) < 0.2  # Should be close to 10

        # Check that values are spread out (variance check)
        sample_variance = sum((x - sample_mean) ** 2 for x in samples) / len(samples)
        assert 3.0 < sample_variance < 5.0  # Should be close to 4.0

    def test_sample_with_zero_variance(self):
        """Test sampling with zero variance (should be constant)."""
        params = GaussianSamplerParams(mean=7.5, variance=0.0)
        settings = GaussianDataSourceSettings(sampler_id="test_4", params=params)
        sampler = GaussianSampler(settings)

        samples = [sampler.sample_one_msg()["value"] for _ in range(10)]

        # All samples should be exactly the mean
        assert all(s == 7.5 for s in samples)

    def test_sample_with_additive_delta(self):
        """Test sampling with additive delta list."""
        params = GaussianSamplerParams(mean=0.0, variance=0.0)  # Zero variance for predictability
        deltas = [1.0, 2.0, 3.0, 4.0, 5.0]
        settings = GaussianDataSourceSettings(
            sampler_id="test_5", params=params, initial_additive_delta_list=deltas
        )
        sampler = GaussianSampler(settings)

        # First 5 samples should have deltas added
        for expected_delta in deltas:
            msg = sampler.sample_one_msg()
            assert msg["value"] == pytest.approx(expected_delta)

        # 6th sample should not have delta (list exhausted)
        msg = sampler.sample_one_msg()
        assert msg["value"] == pytest.approx(0.0)

    def test_sample_with_empty_delta_list(self):
        """Test sampling with empty delta list."""
        params = GaussianSamplerParams(mean=5.0, variance=0.0)
        settings = GaussianDataSourceSettings(
            sampler_id="test_6", params=params, initial_additive_delta_list=[]
        )
        sampler = GaussianSampler(settings)

        msg = sampler.sample_one_msg()
        assert msg["value"] == pytest.approx(5.0)

    def test_sample_with_negative_delta(self):
        """Test sampling with negative additive deltas."""
        params = GaussianSamplerParams(mean=10.0, variance=0.0)
        deltas = [-2.0, -4.0, -6.0]
        settings = GaussianDataSourceSettings(
            sampler_id="test_7", params=params, initial_additive_delta_list=deltas
        )
        sampler = GaussianSampler(settings)

        expected_values = [8.0, 6.0, 4.0]
        for expected_value in expected_values:
            msg = sampler.sample_one_msg()
            assert msg["value"] == pytest.approx(expected_value)

    def test_source_id_uniqueness(self):
        """Test that different sampler_ids create unique source_ids."""
        params = GaussianSamplerParams()
        settings1 = GaussianDataSourceSettings(sampler_id="test_a", params=params)
        settings2 = GaussianDataSourceSettings(sampler_id="test_b", params=params)

        sampler1 = GaussianSampler(settings1)
        sampler2 = GaussianSampler(settings2)

        assert sampler1.source_id != sampler2.source_id
        assert sampler1.source_id == "gaussian_sampler_test_a"
        assert sampler2.source_id == "gaussian_sampler_test_b"
