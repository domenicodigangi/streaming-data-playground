import os

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class TimeSeriesConfig(BaseModel):
    initial_timestamp: str = "2022-01-01"
    time_interval: str = "H"  # Hourly interval
    total_data_points: int = 1000
    anomaly_position: float = 0.5  # Anomaly at 50% of the series
    anomaly_magnitude: float = 5.0

    class Config:
        env_prefix = "TIME_SERIES_"


class TimeSeriesGenerator:
    def __init__(self, params: TimeSeriesConfig):
        self.config = TimeSeriesConfig.parse_obj(
            {key: value for key, value in params.dict().items() if value is not None}
        )

    def generate(self):
        timestamps = pd.date_range(
            start=self.config.initial_timestamp,
            periods=self.config.total_data_points,
            freq=self.config.time_interval,
        )
        values = np.sin(np.linspace(0, 50, self.config.total_data_points))
        anomaly_index = int(
            self.config.anomaly_position * self.config.total_data_points
        )
        values[anomaly_index : anomaly_index + 10] *= self.config.anomaly_magnitude
        return pd.Series(values, index=timestamps)
