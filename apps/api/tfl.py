import requests

from models import StationStatus


class TFLAPI:
    def __init__(self): ...

    def _scale_crowding(self, ratio: float) -> int:
        # ratio = percentageOfBaseline from API (e.g. 0.0017)
        pct = ratio * 100  # convert to actual percent
        pct = max(0, pct)
        # Cap at 200%
        scaled = 1 + 9 * min(pct, 200) / 200
        return round(scaled)

    def get_station_statuses(self, station_id: str) -> list[StationStatus]:
        response = requests.get(f"https://api.tfl.gov.uk/crowding/{station_id}/Live")
        return [
            StationStatus(
                station_id=station_id,
                crowding_level=self._scale_crowding(station["percentageOfBaseline"]),
                last_updated=station["timeUtc"],
            )
            for station in response.json()
        ]
