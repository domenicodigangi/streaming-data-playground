import logging
from itertools import cycle
from typing import List

from simulator.core.data_generators.abstract_sampler import (
    AbstractSampler,
    AbstractSamplerParams,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoundRobinSamplerParams(AbstractSamplerParams):
    hb_senders_ids: List[str] = ["entity_1", "entity_2", "entity_3"]
    hb_frequency_sec: int = 60


class RoundRobinSampler(AbstractSampler):
    def __init__(self, params: RoundRobinSamplerParams | None = None):
        super().__init__(params)
        self.params = params or RoundRobinSamplerParams()
        self._cycle = cycle(self.params.hb_senders_ids)
        self.update_interval_sec()

    def update_interval_sec(self):
        n_hb_sender = len(self.params.hb_senders_ids)
        self.params.interval_sec = self.params.hb_frequency_sec / n_hb_sender

    def sample_one_msg(self) -> str:
        sampled_value = self._get_next()
        logger.debug("Sampled value: %s", sampled_value)
        return f'{{"source_id": {sampled_value} }}'

    def _get_next(self) -> str:
        return next(self._cycle)
