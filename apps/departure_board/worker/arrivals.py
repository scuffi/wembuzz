import requests
from datetime import datetime, timezone

from models import Arrival, ArrivalsResponse, Station


def get_arrivals(station: Station, direction: str = "outbound") -> list[Arrival]:
    response = requests.get(
        f"https://api.tfl.gov.uk/Line/metropolitan,jubilee/Arrivals/{station.stop_point_id}?direction={direction}"
    )

    if response.status_code != 200:
        message = response.json().get("message", "Unknown error")
        raise Exception(f"Failed to get arrivals for station {station.name}: {message}")

    structured_response = [
        ArrivalsResponse.model_validate(item) for item in response.json()
    ]

    return [
        Arrival(
            id=arrival.id,
            line_id=arrival.lineId,
            platform_name=arrival.platformName,
            direction=arrival.direction,
            arrival_time=datetime.fromisoformat(arrival.expectedArrival).astimezone(
                timezone.utc
            ),
            destination_name=arrival.destinationName,
        )
        for arrival in structured_response
    ]
