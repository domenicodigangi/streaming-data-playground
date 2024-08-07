import json
import logging
import random
from datetime import datetime

from simulator.core.data_generators.abstract_sampler import (AbstractSampler,
                                                             AbstractSamplerParams, )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GaussianSamplerParams(AbstractSamplerParams):
    mean: float = 0.1
    variance: float = 1.0


class GaussianSampler(AbstractSampler):
    def __init__(self, params: GaussianSamplerParams | None = None):
        super().__init__(params)
        self.params = params or GaussianSamplerParams()

    def sample_one_msg(self) -> str:
        sampled_value = random.gauss(self.params.mean, self.params.variance ** 0.5)
        logger.debug("Sampled value: %s", sampled_value)
        timestamp = int(datetime.now().timestamp() * 1000)
        msg = {"source_id": "gaussian_sampler", "value": sampled_value,
               "timestamp": timestamp, }
        return json.dumps(msg)
