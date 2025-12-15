from threading import Lock

from models import Arrival
from screen import Screen


class SharedArrivals:
    def __init__(self):
        self.arrivals = {}

    def set_arrivals(self, line_id: str, arrivals: list[Arrival]):
        self.arrivals[line_id] = arrivals

    def get_arrivals(self, line_id: str) -> list[Arrival]:
        return self.arrivals[line_id]

    def get_next_arrival(self, line_id: str) -> Arrival | None:
        """Get the next arrival for a line, rotating the list (move first to end)."""
        arrivals_list = self.arrivals[line_id]

        if not arrivals_list:
            return None

        arrival = arrivals_list.pop(0)
        arrivals_list.append(arrival)
        self.arrivals[line_id] = arrivals_list
        return arrival


shared_arrivals = SharedArrivals()

screen = Screen(width=96, height=48, brightness=100)
screen_lock = Lock()
