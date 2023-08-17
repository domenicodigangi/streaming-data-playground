# from simulator.core.data_generators.time_series_generator import (
#     TimeSeriesConfig,
#     TimeSeriesGenerator,
# )
# from simulator.core.kafka_publisher import KafkaPublisher
# from fastapi import APIRouter, HTTPException
# import logging


# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
# )
# logger = logging.getLogger(__name__)

# router = APIRouter()


# @router.post("/emit_to_kafka")
# def emit_time_series(params: TimeSeriesConfig | None = None):
#     params = params or TimeSeriesConfig()
#     logger.info("Generating time series with parameters: %s", params)
#     time_series_generator = TimeSeriesGenerator(params)
#     time_series = time_series_generator.generate()

#     publisher = KafkaPublisher()

#     for timestamp, value in time_series.items():
#         logger.info("emit: %s: %s", timestamp, value)
#         publisher.emit(timestamp, value)

#     logger.info("Time series generated and published to Kafka")
#     return {
#         "status": "success",
#         "message": "Time series generated and published to Kafka",
#     }
