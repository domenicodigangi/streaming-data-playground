import logging

import uvicorn
from fastapi import FastAPI
from simulator.app.routers.gaussian_data import gaussian_router
from simulator.app.routers.periodic_hb import periodic_hb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "simulator data sampler is running"}


app.include_router(gaussian_router, prefix="/v1/gaussian")
app.include_router(periodic_hb, prefix="/v1/gaussian")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
