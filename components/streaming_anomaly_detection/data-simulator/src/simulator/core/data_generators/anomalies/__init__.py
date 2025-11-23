import logging

import numpy as np
from pydantic import BaseModel, Field, conlist

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDefinition(BaseModel):
    values: conlist(float, min_length=20, max_length=20)
    n_observations: int = Field(..., gt=0)


class AnomalyHelper:
    def __init__(self, anomaly_definition: AnomalyDefinition):
        self.values = anomaly_definition.values
        self.n_observations = anomaly_definition.n_observations

    def generate_list_to_add(self) -> list[float]:
        """
        Rescale the input anomaly values to match the requested number of observations.

        Uses linear interpolation to stretch or compress the 20 input values
        to exactly n_observations values.

        Returns:
            list[float]: Interpolated anomaly values of length n_observations
        """
        if len(self.values) == self.n_observations:
            return self.values

        # Create indices for original values (0 to 19 for 20 values)
        original_indices = np.arange(len(self.values))

        # Create indices for target values (0 to n_observations-1, but scaled to 0-19 range)
        target_indices = np.linspace(0, len(self.values) - 1, self.n_observations)

        # Interpolate values
        interpolated = np.interp(target_indices, original_indices, self.values)

        logger.info(
            f"Rescaled anomaly from {len(self.values)} to {self.n_observations} observations"
        )

        return interpolated.tolist()
