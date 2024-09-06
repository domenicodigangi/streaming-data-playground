import logging
from abc import ABC
from datetime import datetime
from functools import cached_property
from typing import Dict

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbstractSamplerParams(BaseModel):
    interval_sec: float = 0.5

    @cached_property
    def name(self) -> str:
        return "unspecified_sampler"


class AbstractDataSourceSettings(BaseModel):
    sampler_id: str
    params: AbstractSamplerParams
    initial_additive_delta_list: list[float] | None = None  # floats to add to initial 

    # samples 

    @cached_property
    def source_id(self) -> str:
        return f"{self.params.name}_{self.sampler_id}"


class AbstractSampler(ABC):

    def __init__(self, settings: AbstractDataSourceSettings):
        self.params = settings.params
        self.source_id = settings.source_id
        self.initial_additive_delta_list = settings.initial_additive_delta_list

    def sample_one_msg(self) -> Dict:
        sampled_value = self._sample_one_value()
        adjusted_value = self._add_initial_additive_delta(sampled_value)
        logger.debug("Sampled value: %s, adjusted value: %s", sampled_value,
                     adjusted_value)
        return self._format_msg(adjusted_value)

    def _sample_one_value(self) -> float:
        raise NotImplementedError()

    def _add_initial_additive_delta(self, value: float) -> float:
        additive_value = self._next_additive_value()
        if additive_value is None:
            return value
        return value + additive_value

    def _next_additive_value(self) -> float:
        if self.initial_additive_delta_list:
            return self.initial_additive_delta_list.pop(0)

    def _format_msg(self, value: float) -> Dict:
        timestamp = int(datetime.now().timestamp() * 1000)

        return {"source_id": self.source_id, "value": value, "timestamp": timestamp}
