from fastapi import FastAPI
from .api.api_v1 import router as api_v1_router


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}

app.include_router(api_v1_router, prefix="/v1")