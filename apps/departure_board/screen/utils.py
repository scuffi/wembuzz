"""Utility classes for pixel-based display operations."""

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Position:
    """Represents a pixel position (x, y)."""
    x: int
    y: int

    def __add__(self, other: 'Position') -> 'Position':
        """Add two positions together."""
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Position') -> 'Position':
        """Subtract one position from another."""
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: int) -> 'Position':
        """Multiply position by a scalar."""
        return Position(self.x * scalar, self.y * scalar)

    def as_tuple(self) -> Tuple[int, int]:
        """Convert to tuple."""
        return (self.x, self.y)


@dataclass
class Color:
    """Represents an RGB color."""
    r: int
    g: int
    b: int

    def __post_init__(self):
        """Clamp color values to valid range."""
        self.r = max(0, min(255, self.r))
        self.g = max(0, min(255, self.g))
        self.b = max(0, min(255, self.b))

    def as_tuple(self) -> Tuple[int, int, int]:
        """Convert to tuple."""
        return (self.r, self.g, self.b)

    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create color from hex string (e.g., '#FF0000' or 'FF0000')."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        return cls(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )

    @classmethod
    def from_tuple(cls, rgb: Tuple[int, int, int]) -> 'Color':
        """Create color from tuple."""
        return cls(*rgb)


# Common colors
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)


@dataclass
class Region:
    """Represents a rectangular region on the display."""
    x: int
    y: int
    width: int
    height: int

    def contains(self, pos: Position) -> bool:
        """Check if position is within this region."""
        return (self.x <= pos.x < self.x + self.width and
                self.y <= pos.y < self.y + self.height)

    def clip_position(self, pos: Position) -> Optional[Position]:
        """Clip position to region bounds, return None if outside."""
        if not self.contains(pos):
            return None
        return Position(
            max(self.x, min(self.x + self.width - 1, pos.x)),
            max(self.y, min(self.y + self.height - 1, pos.y))
        )

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounds as (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
