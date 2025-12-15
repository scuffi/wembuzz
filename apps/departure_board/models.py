from datetime import datetime
from pydantic import BaseModel


class ArrivalsResponse(BaseModel):
    id: str
    operationType: int
    vehicleId: str
    naptanId: str
    stationName: str
    lineId: str
    lineName: str
    platformName: str
    direction: str
    bearing: str
    destinationNaptanId: str
    destinationName: str
    timestamp: str
    timeToStation: int
    currentLocation: str
    towards: str
    expectedArrival: str
    timeToLive: str
    modeName: str


class StationStatus(BaseModel):
    station_id: str
    crowding_level: int
    last_updated: datetime | None = None


class Station(BaseModel):
    name: str
    naptan: str
    stop_point_id: str


class Arrival(BaseModel):
    id: str
    line_id: str
    platform_name: str
    direction: str
    arrival_time: datetime
    destination_name: str
    index: int | None = None
    time_to_station: int | None = None
