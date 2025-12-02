import requests
from datetime import datetime, timezone

from models import Station, StationStatus


def _scale_crowding(value: float, round_result=True) -> float | int:
    """
    Converts TfL percentageOfBaseline into a 1–10 scale.
    1 = empty, 10 = peak levels.
    """
    score = 1 + (value * 11)

    score = max(1, min(10, score))

    return int(round(score)) if round_result else score


def get_station_statuses(station: Station) -> list[StationStatus]:
    response = requests.get(f"https://api.tfl.gov.uk/crowding/{station.naptan}/Live")
    if response.status_code != 200:
        message = response.json().get("message", "Unknown error")
        raise Exception(
            f"Failed to get station status for station {station.name}: {message}"
        )

    json_response = response.json()

    return StationStatus(
        station_id=station.naptan,
        crowding_level=_scale_crowding(json_response["percentageOfBaseline"]),
        last_updated=datetime.fromisoformat(json_response["timeUtc"]).astimezone(
            timezone.utc
        ),
    )
