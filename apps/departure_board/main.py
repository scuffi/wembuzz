import os
import sys
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout import setup_layout
from schedules import (
    fetch_arrivals_schedule,
    rotate_arrivals_schedule,
    update_crowding_schedule,
    update_time_schedule,
)


if __name__ == "__main__":
    setup_layout()

    scheduler = BackgroundScheduler()

    # Fetch arrivals every minute
    scheduler.add_job(
        fetch_arrivals_schedule, "interval", minutes=1, next_run_time=datetime.now()
    )

    # Rotate secondary arrivals every 5 seconds
    scheduler.add_job(
        rotate_arrivals_schedule,
        "interval",
        seconds=5,
        next_run_time=datetime.now() + timedelta(seconds=1),
    )

    # Update time every second
    scheduler.add_job(
        update_time_schedule, "interval", seconds=1, next_run_time=datetime.now()
    )

    # Update crowding every 5 minutes
    scheduler.add_job(
        update_crowding_schedule, "interval", minutes=5, next_run_time=datetime.now()
    )

    scheduler.start()

    while True:
        time.sleep(1)
