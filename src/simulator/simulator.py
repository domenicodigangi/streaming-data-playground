import random
from typing import Optional

import numpy as np


class AnomalyTimeSeriesSimulator:

    def sample_with_anomaly(self, size: int, anomaly_duration: int, anomaly_std_size: float) -> np.array:
        wn_sample, loc, scale = self.sample_white_noise(size)

        half_duration = anomaly_duration // 2
        anomaly_location = random.choice(range(anomaly_duration, size - + 1))
        wn_sample[anomaly_location - half_duration:anomaly_location + half_duration]

    def sample_white_noise(self, size, rng_seed: Optional[int] = None, loc: int = 0, scale: int = 1) -> np.array:
        rng_seed = rng_seed or random.randint(0, 1000000)
        rng = np.random.RandomState(rng_seed)

        sample = rng.normal(loc=loc, scale=scale, size=size)

        return sample, loc, scale
