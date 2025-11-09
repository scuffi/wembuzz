import json
import requests
from bs4 import BeautifulSoup, Tag

from models import Event
from .venue import Venue

WEBSITE_URL = "https://www.ovoarena.co.uk/events"


class OVOArena(Venue):
    def __init__(self):
        super().__init__("OVO Arena")

    def get_page_content(self) -> str:
        return requests.get(WEBSITE_URL).text

    def get_events(self) -> list[Event]:
        events = []

        soup = BeautifulSoup(self.get_page_content(), "html.parser")
        for tag in soup.find_all("script", {"type": "application/ld+json"}):
            items = self._get_events_from_tag(tag)
            for obj in items:
                if self._is_object_valid_event(obj):
                    title = obj.get("name")
                    description = obj.get("description")
                    start = obj.get("startDate")
                    end = obj.get("endDate")
                    url = obj.get("url")
                    image_url = obj.get("image")
                    status = obj.get("eventStatus")
                    events.append(
                        Event(
                            name=title,
                            description=description,
                            start_date=start,
                            end_date=end,
                            url=url,
                            image_url=image_url,
                            status=status,
                            venue=self.name,
                        )
                    )
        return events

    def _get_events_from_tag(self, tag: Tag) -> list:
        try:
            data = json.loads(tag.string or tag.text or "{}")
        except json.JSONDecodeError:
            # sometimes multiple JSON objects without array
            try:
                payload = "[" + tag.get_text().strip().replace("}\n{", "},{") + "]"
                data = json.loads(payload)
            except Exception:
                return []

        return data if isinstance(data, list) else [data]

    def _is_object_valid_event(self, obj: dict) -> bool:
        return isinstance(obj, dict) and obj.get("@type") in ("Event", ["Event"])
