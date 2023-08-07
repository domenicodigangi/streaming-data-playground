import uvicorn
from composer.api.time_series import router as ts_router
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}


app.include_router(ts_router, prefix="/v1/time_series")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
