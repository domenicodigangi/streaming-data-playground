from fastapi import FastAPI
from composer.api.time_series import router as ts_router


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}


app.include_router(ts_router, prefix="/v1/time_series")
