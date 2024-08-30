from abc import ABC
from functools import cached_property
from typing import Dict

from pydantic import BaseModel


class AbstractSamplerParams(BaseModel):
    interval_sec: float = 0.5

    @cached_property
    def name(self) -> str:
        return "unspecified_sampler"


class AbstractDataSourceSettings(BaseModel):
    sampler_id: str
    params: AbstractSamplerParams

    @cached_property
    def source_id(self) -> str:
        return f"{self.params.name}_{self.sampler_id}"


class AbstractSampler(ABC):

    def __init__(self, settings: AbstractDataSourceSettings):
        self.params = settings.params
        self.source_id = settings.source_id

    def sample_one_msg(self) -> Dict:
        raise NotImplementedError()
