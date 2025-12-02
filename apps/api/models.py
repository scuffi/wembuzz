from datetime import datetime
from pydantic import BaseModel


class LineStatus(BaseModel):
    line: str


class StationStatus(BaseModel):
    station_id: str
    crowding_level: int
    last_updated: datetime | None = None
