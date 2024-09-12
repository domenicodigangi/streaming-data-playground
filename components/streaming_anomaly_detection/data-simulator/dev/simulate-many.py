import asyncio
import logging
from functools import cached_property

import httpx

from simulator.core.data_generators.gaussian_sampler import GaussianSamplerParams


class SimulatorHelper:
    def __init__(self, params: GaussianSamplerParams | None = None,
                 semaphore: asyncio.Semaphore | None = None):
        self.params = params or GaussianSamplerParams()
        self.logger = logging.getLogger(__name__)
        self.semaphore = semaphore or asyncio.Semaphore(20)  # Max 20 concurrent requests

    async def update_gaussian_sampler_simulator_settings(self):
        async with self.semaphore:
            update_url = f"{self.base_simulator_url}/{self.params.sampler_id}/update"
            async with httpx.AsyncClient() as client:
                res = await client.post(update_url,
                                        json={"sampler_id": self.params.sampler_id,
                                              "mean": self.params.mean,
                                              "variance": self.params.variance,
                                              "interval_sec": self.params.interval_sec})
            self.logger.info("Response from simulator: %s", res.text)

    async def stop_gaussian_sampler(self):
        async with self.semaphore:
            stop_url = f"{self.base_simulator_url}/{self.params.sampler_id}/stop"
            async with httpx.AsyncClient() as client:
                response = await client.post(stop_url)
            return response

    @cached_property
    def base_simulator_url(self) -> str:
        return f"http://localhost:8001/v1/gaussian/gaussian_sampler"


async def start_all(n_max: int, n_semaphore: int = 20):
    semaphore = asyncio.Semaphore(n_semaphore)  # Max 20 concurrent requests
    tasks = []

    for i in range(1, n_max):
        simulator_helper = SimulatorHelper(GaussianSamplerParams(sampler_id=i),
                                           semaphore=semaphore)
        tasks.append(
            simulator_helper.update_gaussian_sampler_simulator_settings())  # Uncomment  

    await asyncio.gather(*tasks)


async def stop_all(n_max: int, n_semaphore: int = 20):
    semaphore = asyncio.Semaphore(n_semaphore)  # Max 20 concurrent requests
    tasks = []

    for i in range(1, n_max):
        simulator_helper = SimulatorHelper(GaussianSamplerParams(sampler_id=i),
                                           semaphore=semaphore)
        tasks.append(simulator_helper.stop_gaussian_sampler())

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_all(100))
    asyncio.run(stop_all(100))
