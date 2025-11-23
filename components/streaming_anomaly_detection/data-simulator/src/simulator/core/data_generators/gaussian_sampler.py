import logging
import random
from functools import cached_property

from pydantic import Field, field_validator

from simulator.core.data_generators.abstract_sampler import (AbstractDataSourceSettings,
                                                             AbstractSampler,
                                                             AbstractSamplerParams, )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GaussianSamplerParams(AbstractSamplerParams):
    # Security: Add bounds to prevent abuse and resource exhaustion
    mean: float = Field(default=0.1, ge=-1000.0, le=1000.0, description="Mean of Gaussian distribution")
    variance: float = Field(default=1.0, ge=0.0, le=1000.0, description="Variance (must be non-negative)")

    @field_validator("variance")
    @classmethod
    def validate_variance(cls, v):
        """Security: Ensure variance is non-negative."""
        if v < 0:
            raise ValueError("Variance must be non-negative")
        return v

    @cached_property
    def name(self) -> str:
        return "gaussian_sampler"


class GaussianDataSourceSettings(AbstractDataSourceSettings):
    params: GaussianSamplerParams


class GaussianSampler(AbstractSampler):
    def __init__(self, settings: GaussianDataSourceSettings):
        super().__init__(settings)

    def _sample_one_value(self) -> float:
        return random.gauss(self.params.mean, self.params.variance ** 0.5)
