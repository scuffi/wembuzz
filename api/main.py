import uvicorn
from fastapi import FastAPI
from fastapi_crons import get_cron_router

from models import Event
from events.stadium import Stadium
from events.ovo import OVOArena

app = FastAPI()

app.include_router(get_cron_router(), prefix="/crons")


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/events")
def get_events():
    events: list[Event] = []
    for venue in [OVOArena(), Stadium()]:
        events.extend(venue.get_events())

    events.sort(key=lambda x: x.start_date)

    return {"events": events}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
