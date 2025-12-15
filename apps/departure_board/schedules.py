from datetime import datetime
from loguru import logger

from shared import screen, screen_lock, shared_arrivals
from worker import WembleyPark, get_arrivals, get_station_status


def fetch_arrivals_schedule():
    logger.info("🚂 Fetching arrivals")
    # Get arrivals from worker
    arrivals = get_arrivals(WembleyPark)
    # Update arrivals in screen
    for line_id in arrivals.keys():
        primary_arrival = arrivals[line_id][0]
        # Update arrival #1
        time_diff = int(primary_arrival.time_to_station / 60)
        print(f"🚂 Time diff for {line_id}: {time_diff}")
        with screen_lock:
            screen.get_component(f"{line_id}_primary_station_name").set_text(
                primary_arrival.destination_name
            )
            screen.get_component(f"{line_id}_primary_time_to_arrival").set_text(
                f"~{int(time_diff)}m" if time_diff else "Now"
            )

        # Save later arrivals to SharedArrivals
        shared_arrivals.set_arrivals(line_id, arrivals[line_id][1:])


def update_time_schedule():
    # Update time in screen
    with screen_lock:
        screen.get_component("real_time").set_text(datetime.now().strftime("%H:%M:%S"))


def update_crowding_schedule():
    # Update crowding in screen
    crowding = get_station_status(WembleyPark)
    logger.info(
        f"🚂 Updating crowding for station {WembleyPark.name}: {crowding.crowding_level}"
    )
    with screen_lock:
        screen.get_component("crowding").set_value(crowding.crowding_level)


def rotate_arrivals_schedule():
    # Rotate arrivals based on stored state
    for line_id in shared_arrivals.arrivals.keys():
        next_arrival = shared_arrivals.get_next_arrival(line_id)
        with screen_lock:
            screen.get_component(f"{line_id}_later_train_index").set_text(
                "" if next_arrival is None else f"{next_arrival.index + 1}"
            )
            screen.get_component(f"{line_id}_later_station_name").set_text(
                "" if next_arrival is None else next_arrival.destination_name
            )
            screen.get_component(f"{line_id}_later_time_to_arrival").set_text(
                ""
                if next_arrival is None
                else f"~{int(next_arrival.time_to_station / 60)}m"
            )
