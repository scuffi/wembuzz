from pymongo import MongoClient
from pymongo.collection import Collection

from models import Event
from settings import settings


class MongoDB:
    def __init__(self):
        self._client = MongoClient(settings.mongo_uri)
        self._db = self._client[settings.mongo_db]

    def get_collection(self, name: str) -> Collection:
        return self._db[name]

    def get_new_events(self, events: list[Event]) -> list[Event]:
        """
        Filter out events that already exist in the database based on their URL.
        Returns a list of events whose URLs don't exist in the database.
        """
        event_urls = [event.url for event in events if event.url]

        if not event_urls:
            return events

        collection = self.get_collection("events")
        existing_docs = collection.find(
            {"url": {"$in": event_urls}},
            {"url": 1},  # Only fetch the URL field for efficiency
        )

        existing_urls = {doc["url"] for doc in existing_docs}

        return [event for event in events if event.url not in existing_urls]

    def insert_events(self, events: list[Event]):
        self.get_collection("events").insert_many(
            [event.model_dump() for event in events]
        )
