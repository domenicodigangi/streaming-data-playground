from abc import ABC

from pydantic import BaseModel


class AbstractSamplerParams(BaseModel):
    interval_sec: float = 0.5


class AbstractSampler(ABC):

    def __init__(self, params: AbstractSamplerParams | None = None):
        self.params = params or AbstractSamplerParams()

    def sample_one(self) -> float | str:
        raise NotImplementedError()
