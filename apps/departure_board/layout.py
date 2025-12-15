import os
import sys

from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import screen
from screen import (
    YELLOW,
    Color,
    CrowdingComponent,
    TextComponent,
    Region,
    GREEN,
    WHITE,
    Font,
)


def setup_layout():
    """Example: Dynamically updating components."""

    def create_text(
        screen,
        name,
        text,
        x,
        y,
        width,
        font,
        color=WHITE,
        align="left",
        max_text_length=None,
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
            max_text_length=max_text_length,
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
        """Helper to create and add a crowding component at specific pixel coordinates."""
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

    create_text(
        screen, "jubilee_primary_train_index", "1", 0, 0, 96, font, Color(160, 165, 169)
    )
    create_text(screen, "jubilee_primary_station_name", "", 8, 0, 72, font, YELLOW)
    create_text(
        screen,
        "jubilee_primary_time_to_arrival",
        "",
        72,
        0,
        24,
        font,
        GREEN,
        "right",
    )

    create_text(
        screen, "jubilee_later_train_index", "", 0, 9, 95, font, Color(160, 165, 169)
    )
    create_text(screen, "jubilee_later_station_name", "", 8, 9, 72, font, YELLOW)
    create_text(
        screen, "jubilee_later_time_to_arrival", "", 72, 9, 24, font, GREEN, "right"
    )

    create_text(
        screen,
        "metropolitan_primary_train_index",
        "1",
        0,
        20,
        95,
        font,
        Color(155, 0, 86),
    )
    create_text(
        screen, "metropolitan_primary_station_name", "", 8, 20, 72, font, YELLOW
    )
    create_text(
        screen,
        "metropolitan_primary_time_to_arrival",
        "",
        72,
        20,
        24,
        font,
        GREEN,
        "right",
    )

    create_text(
        screen,
        "metropolitan_later_train_index",
        "",
        0,
        29,
        95,
        font,
        Color(155, 0, 86),
    )
    create_text(screen, "metropolitan_later_station_name", "", 8, 29, 72, font, YELLOW)
    create_text(
        screen,
        "metropolitan_later_time_to_arrival",
        "",
        72,
        29,
        24,
        font,
        GREEN,
        "right",
    )

    create_text(
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

    create_crowding(
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
