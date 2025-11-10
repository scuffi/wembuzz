from abc import ABC, abstractmethod

from models import Event


class Venue(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def get_events(self) -> list[Event]:
        pass

    @abstractmethod
    def get_page_content(self) -> str:
        pass
