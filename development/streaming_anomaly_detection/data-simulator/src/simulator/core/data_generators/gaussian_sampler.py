import json
import logging
import random
from datetime import datetime
from functools import cached_property
from typing import Dict

from simulator.core.data_generators.abstract_sampler import (AbstractSampler,
                                                             AbstractSamplerParams, )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GaussianSamplerParams(AbstractSamplerParams):
    sampler_id: int|None
    mean: float = 0.1
    variance: float = 1.0

    @cached_property
    def source_id(self) -> str:
        return f"gaussian_sampler_{self.sampler_id}"

class GaussianSampler(AbstractSampler):
    def __init__(self, params: GaussianSamplerParams | None = None):
        super().__init__(params)
        self.params = params or GaussianSamplerParams()

    def sample_one_msg(self) -> Dict:
        sampled_value = random.gauss(self.params.mean, self.params.variance ** 0.5)
        logger.debug("Sampled value: %s", sampled_value)
        timestamp = int(datetime.now().timestamp() * 1000)
        msg = {"source_id": self.params.source_id
            , "value": sampled_value,
               "timestamp": timestamp, }
        return msg
