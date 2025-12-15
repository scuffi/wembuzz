from datetime import datetime, timezone
from shared import screen, screen_lock, shared_arrivals
from worker import WembleyPark, get_arrivals, get_station_status


def fetch_arrivals_schedule():
    # Get arrivals from worker
    arrivals = get_arrivals(WembleyPark)
    # Update arrivals in screen
    for line_id in arrivals.keys():
        primary_arrival = arrivals[line_id][0]
        # Update arrival #1
        time_diff = (
            primary_arrival.arrival_time - datetime.now(tz=timezone.utc)
        ).total_seconds() / 60
        with screen_lock:
            screen.get_component(f"{line_id}_primary_station_name").set_text(
                primary_arrival.destination_name
            )
            screen.get_component(f"{line_id}_primary_time_to_arrival").set_text(
                f"~{int(time_diff)}m"
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
    with screen_lock:
        screen.get_component("crowding").set_value(crowding.crowding_level)


def rotate_arrivals_schedule():
    # Rotate arrivals based on stored state
    # Get all arrivals from shared dict -> get next arrival -> update UI with next arrival
    for line_id in shared_arrivals.arrivals.keys():
        next_arrival = shared_arrivals.get_next_arrival(line_id)
        with screen_lock:
            screen.get_component(f"{line_id}_later_train_index").set_text(
                next_arrival.index + 1
            )
            screen.get_component(f"{line_id}_later_station_name").set_text(
                next_arrival.destination_name
            )
            time_diff = (
                next_arrival.arrival_time - datetime.now(tz=timezone.utc)
            ).total_seconds() / 60
            screen.get_component(f"{line_id}_later_time_to_arrival").set_text(
                f"~{int(time_diff)}m"
            )
