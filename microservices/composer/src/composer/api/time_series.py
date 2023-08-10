from composer.core.event_publisher import EventPublisher
from composer.core.time_series_generator import TimeSeriesConfig, TimeSeriesGenerator
from fastapi import APIRouter, HTTPException
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/emit_to_kafka")
def emit_time_series(params: TimeSeriesConfig | None = None):
    try:
        params = params or TimeSeriesConfig()
        logger.info("Generating time series with parameters: %s", params)
        time_series_generator = TimeSeriesGenerator(params)
        time_series = time_series_generator.generate()

        publisher = EventPublisher(target="kafka")

        for timestamp, value in time_series.items():
            publisher.emit(timestamp, value)

        logger.info("Time series generated and published to Kafka")
        return {
            "status": "success",
            "message": "Time series generated and published to Kafka",
        }
    except Exception as e:
        logger.error("An error occurred while emitting time series: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
