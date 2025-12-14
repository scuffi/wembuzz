"""LED RGB Matrix Display API for creating layouts and components."""

from .screen import Screen, Font
from .layouts import Layout
from .components import (
    Component,
    TextComponent,
    AnimationType,
    RectangleComponent,
    LineComponent,
    PixelComponent,
    BorderComponent,
    CrowdingComponent,
)
from .utils import (
    Position,
    Color,
    Region,
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN,
    MAGENTA,
)

__all__ = [
    "Screen",
    "Font",
    "Layout",
    "Component",
    "TextComponent",
    "AnimationType",
    "RectangleComponent",
    "LineComponent",
    "PixelComponent",
    "BorderComponent",
    "CrowdingComponent",
    "Position",
    "Color",
    "Region",
    "BLACK",
    "WHITE",
    "RED",
    "GREEN",
    "BLUE",
    "YELLOW",
    "CYAN",
    "MAGENTA",
]
