"""Example usage of the LED Display API."""

import time
import sys
import os

os.environ["LED_ENV"] = "emulator"
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screen import (
    YELLOW,
    Color,
    Screen,
    TextComponent,
    AnimationType,
    RectangleComponent,
    PixelComponent,
    BorderComponent,
    Region,
    RED,
    GREEN,
    BLUE,
    WHITE,
    Font,
)


def example_basic():
    """Basic example: Simple text and shapes."""
    # Create screen (64x32 is common for LED matrices)
    screen = Screen(width=64, height=32, brightness=50)

    # Create a layout
    layout = screen.create_layout()

    # Define regions
    layout.define_region("header", Region(0, 0, 64, 8))
    layout.define_region("content", Region(0, 8, 64, 24))

    # Add components
    header_bg = RectangleComponent(layout.get_region("header"), color=BLUE, fill=True)
    screen.add_component("header_bg", header_bg, "header")

    header_text = TextComponent(
        layout.get_region("header"),
        text="Hello!",
        color=WHITE,
        align="center",
        vertical_align="center",
    )
    screen.add_component("header_text", header_text, "header")

    # Render
    screen.render()

    # Update text after 2 seconds
    time.sleep(2)
    header_text.set_text("Updated!")
    screen.update()

    time.sleep(2)


def example_split_layout():
    """Example: Using layout splitting."""
    screen = Screen(width=64, height=32, brightness=50)
    layout = screen.create_layout()

    # Split screen into 3 horizontal sections
    layout.define_region("main", Region(0, 0, 64, 32))
    top, middle, bottom = layout.split_horizontal("main", 20, -1, 20)

    # Add components to each section
    top_rect = RectangleComponent(layout.get_region(top), color=RED, fill=True)
    screen.add_component("top", top_rect, top)

    middle_rect = RectangleComponent(layout.get_region(middle), color=GREEN, fill=True)
    screen.add_component("middle", middle_rect, middle)

    bottom_rect = RectangleComponent(layout.get_region(bottom), color=BLUE, fill=True)
    screen.add_component("bottom", bottom_rect, bottom)

    screen.render()
    time.sleep(2)


def example_dynamic_updates():
    """Example: Dynamically updating components."""
    screen = Screen(width=96, height=48, brightness=100)

    def create_text_line(
        screen, name, text, x, y, width, font, color=WHITE, align="left"
    ):
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

    # Create a text component
    font = Font()
    font.LoadFont("./apps/departure_board/font.bdf")

    create_text_line(screen, "line1", "Wembley Park", 0, 0, 96, font)
    create_rectangle(
        screen,
        "jubes",
        0,
        10,
        width=5,
        height=font.height,
        color=Color(160, 165, 169),
    )
    create_text_line(screen, "station_name", "Stanmore", 8, 10, 72, font, YELLOW)
    create_text_line(screen, "time_to_arrival", "~2m", 72, 10, 24, font, GREEN, "right")
    # text_region = Region(0, 0, 96, 48)
    # text_component = TextComponent(
    #     text_region,
    #     text="Wembley Park",
    #     color=WHITE,
    #     align="left",
    #     vertical_align="top",
    #     font=font,
    # )
    # screen.add_component("counter", text_component)

    screen.render()
    time.sleep(10)


def example_custom_pixels():
    """Example: Using custom pixel component."""
    screen = Screen(width=64, height=32, brightness=50)

    # Create pixel component
    pixel_region = Region(0, 0, 32, 32)
    pixel_data = [
        (x, y, RED if (x + y) % 2 == 0 else BLUE) for x in range(32) for y in range(32)
    ]

    pixel_component = PixelComponent(pixel_region, pixel_data=pixel_data)
    screen.add_component("pixels", pixel_component)

    screen.render()
    time.sleep(2)


def example_complex_layout():
    """Example: Complex layout with multiple components."""
    screen = Screen(width=96, height=48, brightness=100)
    layout = screen.create_layout()

    # Create a grid layout
    layout.define_region("grid", Region(0, 0, 96, 48))

    # Split into 2x2 grid
    top_row, bottom_row = layout.split_vertical("grid", -1, -1)
    top_left, top_right = layout.split_horizontal(top_row, -1, -1)
    bottom_left, bottom_right = layout.split_horizontal(bottom_row, -1, -1)

    # Add different components to each quadrant
    colors = [RED, GREEN, BLUE, YELLOW]
    regions = [top_left, top_right, bottom_left, bottom_right]

    for i, (region_name, color) in enumerate(zip(regions, colors)):
        rect = RectangleComponent(
            layout.get_region(region_name),
            color=color,
            fill=True,
            border_width=2,
            border_color=WHITE,
        )
        screen.add_component(f"quad_{i}", rect, region_name)

        font = Font()
        font.LoadFont("./apps/departure_board/font.bdf")
        text = TextComponent(
            layout.get_region(region_name),
            text=f"Q{i+1}",
            font=font,
            color=WHITE,
            align="center",
            vertical_align="center",
        )
        screen.add_component(f"text_{i}", text, region_name)

    screen.render()
    time.sleep(3)


def example_animated_border():
    """Example: Animated rainbow border with rotating dashes."""
    screen = Screen(width=96, height=48, brightness=100)

    # Create animated border component
    border_region = Region(0, 0, 96, 48)
    border = BorderComponent(
        border_region,
        num_dashes=4,  # Number of dashes around the border
        dash_length=8,  # Length of each dash
        dash_gap=3,  # Gap between dashes
        speed=2.0,  # Animation speed (higher = faster)
    )
    screen.add_component("border", border)

    # Optional: Add some content inside
    font = Font()
    font.LoadFont("./apps/departure_board/font.bdf")

    text_region = Region(10, 20, 76, font.height)
    text = TextComponent(
        text_region,
        text="Animated Border!",
        color=WHITE,
        align="center",
        vertical_align="top",
        font=font,
    )
    screen.add_component("text", text)

    # Animate for 10 seconds
    print("Running animated border example...")
    start_time = time.time()
    while time.time() - start_time < 10:
        screen.update()  # Update only dirty components
        time.sleep(0.05)  # ~20 FPS for smooth animation


def example_text_animations():
    """Example: Demonstrating all text animation types."""
    screen = Screen(width=96, height=48, brightness=100)

    # Load font
    font = Font()
    font.LoadFont("./apps/departure_board/font.bdf")

    # Create text component
    text_region = Region(0, 0, 96, 8)
    text_component = TextComponent(
        text_region,
        text="Initial Text",
        color=WHITE,
        align="center",
        vertical_align="center",
        font=font,
    )
    screen.add_component("text", text_component)

    # Initial render
    screen.render()
    time.sleep(1)

    print("Running text animations demo...")
    print("1. Push animation...")
    text_component.set_text(
        "Push Animation!", animation=AnimationType.PUSH, duration=40
    )
    # Wait for animation to complete
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("2. Fade animation...")
    text_component.set_text("Fade In Effect", animation=AnimationType.FADE, duration=30)
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("3. Typewriter animation...")
    text_component.set_text(
        "Typewriter Effect!", animation=AnimationType.TYPEWRITER, duration=60
    )
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("4. Slide from left...")
    text_component.set_text(
        "Slide Left", animation=AnimationType.SLIDE_LEFT, duration=30
    )
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("5. Slide from right...")
    text_component.set_text(
        "Slide Right", animation=AnimationType.SLIDE_RIGHT, duration=30
    )
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("6. Slide from top...")
    text_component.set_text(
        "Slide Down", animation=AnimationType.SLIDE_DOWN, duration=30
    )
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("7. Slide from bottom...")
    text_component.set_text("Slide Up", animation=AnimationType.SLIDE_UP, duration=30)
    while text_component.is_animating():
        screen.update()
        time.sleep(0.05)
    time.sleep(0.5)

    print("8. Multiple rapid animations...")
    animations = [
        ("Hello", AnimationType.FADE, 20),
        ("World", AnimationType.PUSH, 25),
        ("Test", AnimationType.TYPEWRITER, 30),
        ("Done!", AnimationType.SLIDE_LEFT, 20),
    ]

    for text, anim_type, duration in animations:
        text_component.set_text(text, animation=anim_type, duration=duration)
        while text_component.is_animating():
            screen.update()
            time.sleep(0.05)
        time.sleep(0.3)

    print("Text animations demo complete!")


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

    # Create animated border component
    # border_region = Region(0, 0, 96, 48)
    # border = BorderComponent(
    #     border_region,
    #     num_dashes=4,  # Number of dashes around the border
    #     dash_length=12,  # Length of each dash
    #     dash_gap=3,  # Gap between dashes
    #     speed=2.0,  # Animation speed (higher = faster)
    # )
    # screen.add_component("border", border)

    # Create a text component
    font = Font()
    font.LoadFont("./apps/departure_board/font.bdf")

    # create_text(screen, "line1", "Wembley Park", 0, 0, 95, font)
    # create_rectangle(
    #     screen,
    #     "jubes",
    #     1,
    #     10,
    #     width=5,
    #     height=font.height,
    #     color=Color(160, 165, 169),
    # )
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

    met_station_number = create_text(
        screen, "met_next_station", "1", 0, 20, 95, font, Color(155, 0, 86)
    )
    met_station_name = create_text(
        screen, "met_station_name_second", "Aldgate", 8, 20, 72, font, YELLOW
    )
    met_time_to_arrival = create_text(
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
    # Set environment variable for emulator testing

    # print("Running basic example...")
    # example_basic()

    # print("Running split layout example...")
    # example_split_layout()

    print("Running dynamic updates example...")
    # example_dynamic_updates()

    # print("Running custom pixels example...")
    # example_custom_pixels()

    # print("Running complex layout example...")
    # example_complex_layout()
    # example_animated_border()

    # example_text_animations()

    planned_layout()
