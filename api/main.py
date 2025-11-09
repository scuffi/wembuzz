import uvicorn
from fastapi import FastAPI
from fastapi_crons import get_cron_router

from events.ovo import OVOArena

app = FastAPI()

app.include_router(get_cron_router(), prefix="/crons")


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/events")
def get_events():
    venue1 = OVOArena()
    return {"events": venue1.get_events()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
