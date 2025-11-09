import requests
from models import Event

from .venue import Venue

WEBSITE_URL = "https://www.wembleystadium.com/events"


class Stadium(Venue):
    def __init__(self):
        super().__init__("Wembley Stadium")

    def get_events(self) -> list[Event]:
        return []

    def get_page_content(self) -> str:
        return requests.get(WEBSITE_URL).text
