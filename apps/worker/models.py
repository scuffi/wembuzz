from datetime import datetime
from pydantic import BaseModel


class Event(BaseModel):
    name: str
    description: str
    status: str
    start_date: datetime
    end_date: datetime
    url: str
    image_url: str
    venue: str
    crowding_level: int | None = None
