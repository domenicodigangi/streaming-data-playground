from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class TimeSeriesParameters(BaseModel):
    initial_timestamp: str = None
    time_interval: str = None
    total_data_points: int = None
    anomaly_position: float = None
    anomaly_magnitude: float = None

class TimeSeriesGenerator:
    def __init__(self, params: TimeSeriesParameters):
        self.config = TimeSeriesConfig.parse_obj({key: value for key, value in params.dict().items() if value is not None})

    def generate(self):
        timestamps = pd.date_range(
            start=self.config.initial_timestamp,
            periods=self.config.total_data_points,
            freq=self.config.time_interval
        )
        values = np.sin(np.linspace(0, 50, self.config.total_data_points))
        anomaly_index = int(self.config.anomaly_position * self.config.total_data_points)
        values[anomaly_index:anomaly_index+10] *= self.config.anomaly_magnitude
        return pd.Series(values, index=timestamps)
