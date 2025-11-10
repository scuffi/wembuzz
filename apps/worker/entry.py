from dotenv import load_dotenv
from events import OVOArena, Stadium
from crowding.ai_estimator import estimate_crowding
from models import Event


def main():
    events: list[Event] = []
    for venue in [OVOArena(), Stadium()]:
        events.extend(venue.get_events())

    events.sort(key=lambda x: x.start_date)
    for event in events:
        event.crowding_level = estimate_crowding(event)
        print(event.name)
        print(event.crowding_level)


if __name__ == "__main__":
    load_dotenv(verbose=True)
    main()
