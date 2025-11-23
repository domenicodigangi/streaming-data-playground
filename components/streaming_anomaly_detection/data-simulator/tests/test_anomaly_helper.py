"""Unit tests for AnomalyHelper and anomaly rescaling functionality."""
import pytest

from simulator.core.data_generators.anomalies import AnomalyDefinition, AnomalyHelper


class TestAnomalyDefinition:
    """Test AnomalyDefinition model validation."""

    def test_valid_anomaly_definition(self):
        """Test creating a valid anomaly definition."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=100)
        assert len(anomaly.values) == 20
        assert anomaly.n_observations == 100

    def test_invalid_values_length_too_short(self):
        """Test that values list must be exactly 20 elements."""
        with pytest.raises(Exception):  # Pydantic validation error
            AnomalyDefinition(values=[1.0, 2.0, 3.0], n_observations=10)

    def test_invalid_values_length_too_long(self):
        """Test that values list must be exactly 20 elements."""
        values = [float(i) for i in range(25)]
        with pytest.raises(Exception):  # Pydantic validation error
            AnomalyDefinition(values=values, n_observations=10)

    def test_invalid_n_observations_zero(self):
        """Test that n_observations must be positive."""
        values = [float(i) for i in range(20)]
        with pytest.raises(Exception):  # Pydantic validation error
            AnomalyDefinition(values=values, n_observations=0)

    def test_invalid_n_observations_negative(self):
        """Test that n_observations must be positive."""
        values = [float(i) for i in range(20)]
        with pytest.raises(Exception):  # Pydantic validation error
            AnomalyDefinition(values=values, n_observations=-5)


class TestAnomalyHelper:
    """Test AnomalyHelper rescaling functionality."""

    def test_no_rescaling_needed(self):
        """Test when n_observations equals input length (20)."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=20)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 20
        assert result == values

    def test_upscale_to_double(self):
        """Test rescaling from 20 to 40 observations."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=40)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 40
        # First and last values should be preserved
        assert result[0] == pytest.approx(0.0)
        assert result[-1] == pytest.approx(19.0)
        # Values should be monotonically increasing (since input is 0..19)
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))

    def test_downscale_to_half(self):
        """Test rescaling from 20 to 10 observations."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=10)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 10
        # First and last values should be preserved
        assert result[0] == pytest.approx(0.0)
        assert result[-1] == pytest.approx(19.0)
        # Values should be monotonically increasing
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))

    def test_rescale_to_large_number(self):
        """Test rescaling to a much larger number (100)."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=100)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 100
        assert result[0] == pytest.approx(0.0)
        assert result[-1] == pytest.approx(19.0)

    def test_rescale_to_small_number(self):
        """Test rescaling to a smaller number (5)."""
        values = [float(i) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=5)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 5
        assert result[0] == pytest.approx(0.0)
        assert result[-1] == pytest.approx(19.0)

    def test_rescale_constant_values(self):
        """Test rescaling when all input values are the same."""
        values = [5.0] * 20
        anomaly = AnomalyDefinition(values=values, n_observations=50)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 50
        # All values should be approximately 5.0
        assert all(abs(v - 5.0) < 0.001 for v in result)

    def test_rescale_negative_values(self):
        """Test rescaling with negative values."""
        values = [float(i - 10) for i in range(20)]  # -10 to 9
        anomaly = AnomalyDefinition(values=values, n_observations=30)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 30
        assert result[0] == pytest.approx(-10.0)
        assert result[-1] == pytest.approx(9.0)

    def test_rescale_preserves_pattern(self):
        """Test that rescaling preserves the general pattern of the data."""
        # Create a sine-like pattern
        import math

        values = [math.sin(i * math.pi / 10) for i in range(20)]
        anomaly = AnomalyDefinition(values=values, n_observations=40)
        helper = AnomalyHelper(anomaly)

        result = helper.generate_list_to_add()

        assert len(result) == 40
        # The pattern should still have a maximum around the middle
        max_idx = result.index(max(result))
        assert 15 < max_idx < 25  # Should be roughly in the middle third
