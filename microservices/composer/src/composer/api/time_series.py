
from fastapi import APIRouter

router = APIRouter()


# {
#     "initial_timestamp": "2022-02-01",
#     "time_interval": "2H",
#     "total_data_points": 500,
#     "anomaly_position": 0.4,
#     "anomaly_magnitude": 3.0
# }

@router.post("/trigger-time-series")
def trigger_time_series(params: TimeSeriesParameters):
    try:
        time_series_generator = TimeSeriesGenerator(params)
        time_series = time_series_generator.generate()

        publisher = EventPublisher(target="kafka")

        for timestamp, value in time_series.iteritems():
            publisher.emit(timestamp, value)

        return {"status": "success", "message": "Time series generated and published to Kafka"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
