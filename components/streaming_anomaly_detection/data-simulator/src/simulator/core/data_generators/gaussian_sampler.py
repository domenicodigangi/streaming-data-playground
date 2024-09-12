import logging
import random
from functools import cached_property

from simulator.core.data_generators.abstract_sampler import (AbstractDataSourceSettings,
                                                             AbstractSampler,
                                                             AbstractSamplerParams, )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GaussianSamplerParams(AbstractSamplerParams):
    mean: float = 0.1
    variance: float = 1.0

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
