import env  # noqa: F401
from datetime import datetime, timedelta, timezone

from logger import logger
from events import OVOArena, Stadium
from crowding.ai_estimator import estimate_crowding
from models import Event
from database import MongoDB
from settings import settings


def main():
    logger.info("Starting event collection")
    unfiltered_events: list[Event] = []
    for venue in [OVOArena(), Stadium()]:
        unfiltered_events.extend(venue.get_events())

    logger.info(f"Found {len(unfiltered_events)} events")

    # Filter out events where start_date is more than 7 days from now
    cutoff_date = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.event_cutoff_days
    )
    events = [event for event in unfiltered_events if event.start_date <= cutoff_date]

    logger.info(
        f"Filtered out {len(unfiltered_events) - len(events)} events with a start date more than {settings.event_cutoff_days} days from now "
    )

    events.sort(key=lambda x: x.start_date)

    db = MongoDB()
    new_events = db.get_new_events(events)

    logger.info(f"Kept {len(new_events)} new events")

    for event in new_events:
        event.crowding_level = estimate_crowding(event)
        logger.info(f"{event.name} - {event.crowding_level}")

    # Only insert the new events into the DB
    if new_events:
        db.insert_events(new_events)
        logger.info("Inserted new events into the database")


if __name__ == "__main__":
    main()
