import logging

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
        return self.values  # TODO need to rescale to required n observations
