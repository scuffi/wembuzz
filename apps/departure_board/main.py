import time

from screen import (
    YELLOW,
    Color,
    Screen,
    TextComponent,
    AnimationType,
    RectangleComponent,
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

    def create_rectangle(screen, name, x, y, width, height, color=WHITE):
        """Helper to create and add a rectangle at specific pixel coordinates."""
        region = Region(x, y, width, height)
        component = RectangleComponent(
            region,
            color=color,
            fill=True,
        )
        screen.add_component(name, component)
        return component

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
        "10:00:36",
        0,
        40,
        96,
        font,
        WHITE,
        "right",
    )

    screen.render()

    # Time-based scheduling - no threading needed
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
            station_number.set_text(
                "2", animation=AnimationType.SLIDE_DOWN, duration=20
            )
            station_name.set_text(
                "Stanmore", animation=AnimationType.SLIDE_DOWN, duration=20
            )
            time_to_arrival.set_text(
                "~6m", animation=AnimationType.SLIDE_DOWN, duration=20
            )
        else:
            station_number.set_text(
                "3", animation=AnimationType.SLIDE_DOWN, duration=20
            )
            station_name.set_text(
                "Aldgate", animation=AnimationType.SLIDE_DOWN, duration=20
            )
            time_to_arrival.set_text(
                "~10m", animation=AnimationType.SLIDE_DOWN, duration=20
            )

    def update_time():
        """Update the real-time clock display."""
        from datetime import datetime

        current_time_str = datetime.now().strftime("%H:%M:%S")
        real_time.set_text(current_time_str)

    # Initialize time display
    update_time()

    print("Running animated border example...")
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

        # Render loop - runs at ~50 FPS
        screen.update()  # Update only dirty components
        time.sleep(0.02)  # ~50 FPS for smooth


if __name__ == "__main__":
    planned_layout()
