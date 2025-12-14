import time
import os
import sys

from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screen import (
    YELLOW,
    Color,
    CrowdingComponent,
    Screen,
    TextComponent,
    Region,
    GREEN,
    WHITE,
    Font,
)

# if __name__ == "__main__":
#     from worker import get_arrivals, get_station_statuses, WembleyPark

#     arrivals = get_arrivals(WembleyPark)
#     print(arrivals)
#     station_statuses = get_station_statuses(WembleyPark)
#     print(station_statuses)


def planned_layout():
    """Example: Dynamically updating components."""
    screen = Screen(width=96, height=48, brightness=100)

    def create_text(screen, name, text, x, y, width, font, color=WHITE, align="left"):
        """Helper to create and add a text line at specific pixel coordinates."""
        region = Region(x, y, width, font.height)
        component = TextComponent(
            region,
            text=text,
            color=color,
            align=align,
            vertical_align="top",
            font=font,
        )
        screen.add_component(name, component)
        return component

    def create_crowding(
        screen,
        name,
        x,
        y,
        width,
        value=0,
        colours=None,
        inactive_color=Color(40, 40, 40),
    ):
        crowding_region = Region(x, y, width, font.height)
        crowding = CrowdingComponent(
            crowding_region,
            font=font,
            value=value,  # Start with 3 out of 5 icons lit
            level_colors=colours,  # Dynamic colors based on level
            inactive_color=inactive_color,  # Dark grey
            spacing=1,
            align="left",
        )
        screen.add_component(name, crowding)
        return crowding

    font = Font()
    font.LoadFont("./apps/departure_board/font.bdf")

    create_text(screen, "line_num", "1", 0, 0, 96, font, Color(160, 165, 169))
    create_text(screen, "station_name", "Stanmore", 8, 0, 72, font, YELLOW)
    create_text(screen, "time_to_arrival", "~2m", 72, 0, 24, font, GREEN, "right")

    station_number = create_text(
        screen, "next_station", "2", 0, 9, 95, font, Color(160, 165, 169)
    )
    station_name = create_text(
        screen, "station_name_second", "Stanmore", 8, 9, 72, font, YELLOW
    )
    time_to_arrival = create_text(
        screen, "time_to_arrival_second", "~6m", 72, 9, 24, font, GREEN, "right"
    )

    create_text(screen, "met_next_station", "1", 0, 20, 95, font, Color(155, 0, 86))
    create_text(screen, "met_station_name_second", "Aldgate", 8, 20, 72, font, YELLOW)
    create_text(
        screen, "met_time_to_arrival_second", "~10m", 72, 20, 24, font, GREEN, "right"
    )

    met_station_number = create_text(
        screen, "met_next_station_dynamic", "2", 0, 29, 95, font, Color(155, 0, 86)
    )
    met_station_name = create_text(
        screen, "met_station_name_dynamic", "Aldgate", 8, 29, 72, font, YELLOW
    )
    met_time_to_arrival = create_text(
        screen,
        "met_time_to_arrival_second_dynamic",
        "~16m",
        72,
        29,
        24,
        font,
        GREEN,
        "right",
    )

    real_time = create_text(
        screen,
        "real_time",
        datetime.now().strftime("%H:%M:%S"),
        48,
        40,
        48,
        font,
        WHITE,
        "right",
    )

    crowding = create_crowding(
        screen,
        "crowding",
        0,
        40,
        48,
        3,
        colours={
            1: Color(0, 200, 0),
            2: Color(150, 200, 0),
            3: Color(255, 200, 0),
            4: Color(255, 100, 0),
            5: Color(255, 0, 0),
        },
        inactive_color=Color(40, 40, 40),
    )

    # Initial render
    screen.render()

    # Time-based scheduling - components will sync themselves when they change
    last_update_time = time.time()
    last_time_update = time.time()
    update_interval = 5.0  # Run update every 5 seconds
    time_update_interval = 1.0  # Update time every 1 second
    iteration = 0

    def update_task():
        """Update task that runs every 5 seconds."""
        nonlocal iteration
        iteration += 1

        if iteration % 2 == 0:
            station_number.set_text("2", animation=None, duration=20)
            station_name.set_text("Stanmore", animation=None, duration=20)
            time_to_arrival.set_text("~6m", animation=None, duration=20)
        else:
            station_number.set_text("3", animation=None, duration=20)
            station_name.set_text("Aldgate", animation=None, duration=20)
            time_to_arrival.set_text("~10m", animation=None, duration=20)

    def update_time():
        """Update the real-time clock display."""
        current_time_str = datetime.now().strftime("%H:%M:%S")
        real_time.set_text(current_time_str)

    # Initialize time display
    update_time()

    # Main loop - just check timers, components handle their own rendering
    while True:
        current_time = time.time()

        # Check if it's time to run the update task (every 5 seconds)
        if current_time - last_update_time >= update_interval:
            update_task()
            last_update_time = current_time

        # Check if it's time to update the clock (every 1 second)
        if current_time - last_time_update >= time_update_interval:
            update_time()
            last_time_update = current_time

        # No render loop! Components sync themselves when they change.
        # Just sleep to avoid busy-waiting
        time.sleep(0.1)  # Check timers every 100ms


if __name__ == "__main__":
    planned_layout()
