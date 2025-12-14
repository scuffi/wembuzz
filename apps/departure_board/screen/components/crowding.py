"""Crowding indicator component for displaying crowding levels with icons."""

from typing import Optional, List, Tuple, Dict
from ..utils import Color, Region, Position
from .base import Component


# Default color scheme - green to red gradient based on crowding level
DEFAULT_LEVEL_COLORS: Dict[int, Color] = {
    1: Color(0, 200, 0),  # Green - low crowding
    2: Color(150, 200, 0),  # Yellow-green
    3: Color(255, 200, 0),  # Yellow/amber - medium crowding
    4: Color(255, 100, 0),  # Orange
    5: Color(255, 0, 0),  # Red - high crowding
}


class CrowdingComponent(Component):
    """Component for displaying crowding level with 5 icons."""

    # Unicode character for the icon (from loaded font)
    ICON_CHAR = "\u0002"

    def __init__(
        self,
        region: Region,
        font=None,
        value: int = 0,
        level_colors: Optional[Dict[int, Color]] = None,
        inactive_color: Color = Color(50, 50, 50),  # Dark grey for inactive
        background_color: Optional[Color] = None,
        spacing: int = 1,  # Spacing between icons
        align: str = "center",  # "left", "center", "right"
        visible: bool = True,
    ):
        """
        Initialize a crowding component.

        Args:
            region: The region this component occupies
            font: Font object (from rgbmatrix.graphics.Font or similar)
            value: Current crowding level (0-5, 0 = none active, 5 = all active)
            level_colors: Dict mapping crowding level (1-5) to Color.
                          All active icons use the color for the current value.
                          If None, uses default green-to-red gradient.
            inactive_color: Color for inactive (dim) icons
            background_color: Optional background color
            spacing: Pixel spacing between icons
            align: Horizontal alignment ("left", "center", "right")
            visible: Whether the component is visible
        """
        super().__init__(region, background_color, visible)
        self.font = font
        self._value = max(0, min(5, value))  # Clamp to 0-5
        self.level_colors = (
            level_colors if level_colors is not None else DEFAULT_LEVEL_COLORS.copy()
        )
        self.inactive_color = inactive_color
        self.spacing = spacing
        self.align = align
        self._needs_redraw = True

    @property
    def value(self) -> int:
        """Get the current crowding value."""
        return self._value

    def set_value(self, value: int) -> None:
        """
        Set the crowding value (0-5).

        Icons with index <= value will be colored with the color from level_colors
        corresponding to the current value. Icons with index > value will be
        colored with inactive_color.

        Args:
            value: Crowding level from 0 (none active) to 5 (all active)
        """
        clamped_value = max(0, min(5, value))
        if self._value != clamped_value:
            self._value = clamped_value
            self._needs_redraw = True
            self.mark_dirty()
            self._sync()

    def set_level_color(self, level: int, color: Color) -> None:
        """
        Set the color for a specific crowding level.

        Args:
            level: Crowding level (1-5)
            color: Color to use when crowding is at this level
        """
        if 1 <= level <= 5:
            self.level_colors[level] = color
            self._needs_redraw = True
            self.mark_dirty()
            self._sync()

    def set_level_colors(self, level_colors: Dict[int, Color]) -> None:
        """
        Set all level colors at once.

        Args:
            level_colors: Dict mapping crowding level (1-5) to Color
        """
        self.level_colors = level_colors.copy()
        self._needs_redraw = True
        self.mark_dirty()
        self._sync()

    def set_inactive_color(self, color: Color) -> None:
        """Update the inactive (dim) icon color."""
        if self.inactive_color != color:
            self.inactive_color = color
            self._needs_redraw = True
            self.mark_dirty()
            self._sync()

    def set_align(self, align: str) -> None:
        """
        Update horizontal alignment.

        Args:
            align: Horizontal alignment ("left", "center", "right")
        """
        if self.align != align:
            self.align = align
            self._needs_redraw = True
            self.mark_dirty()
            self._sync()

    def _get_active_color(self) -> Color:
        """Get the active color based on current value."""
        if self._value == 0:
            # No active icons, return inactive color as fallback
            return self.inactive_color
        # Look up the color for the current crowding level
        return self.level_colors.get(self._value, Color(255, 200, 0))

    def _get_icon_width(self) -> int:
        """Get the width of a single icon character."""
        if self.font:
            return self.font.CharacterWidth(ord(self.ICON_CHAR))
        return 5  # Default fallback

    def _get_font_baseline(self) -> int:
        """Get font baseline offset."""
        if not self.font:
            return 0

        if hasattr(self.font, "baseline"):
            return self.font.baseline

        if hasattr(self.font, "headers"):
            return self.font.headers.get("fbby", 0) + self.font.headers.get(
                "fbbyoff", 0
            )

        if hasattr(self.font, "height"):
            return self.font.height

        return 8  # Default fallback

    def _calculate_start_position(self) -> Tuple[int, int]:
        """Calculate the starting position for rendering icons based on alignment."""
        icon_width = self._get_icon_width()
        total_width = (icon_width * 5) + (self.spacing * 4)

        # Horizontal alignment
        if self.align == "center":
            x = self.region.x + (self.region.width - total_width) // 2
        elif self.align == "right":
            x = self.region.x + self.region.width - total_width
        else:  # "left"
            x = self.region.x

        # Vertical positioning using baseline
        baseline = self._get_font_baseline()
        font_height = (
            self.font.height if (self.font and hasattr(self.font, "height")) else 8
        )
        y = self.region.y + (self.region.height - font_height) // 2 + baseline

        return (x, y)

    def render(self, canvas) -> None:
        """Render the crowding icons to the canvas."""
        if not self.visible:
            return

        # Clear region with background color
        clear_color = (
            self.background_color.as_tuple() if self.background_color else (0, 0, 0)
        )
        for y in range(self.region.y, self.region.y + self.region.height):
            for x in range(self.region.x, self.region.x + self.region.width):
                canvas.SetPixel(x, y, clear_color[0], clear_color[1], clear_color[2])

        if not self.font:
            return

        import os

        if os.environ.get("LED_ENV") == "emulator":
            from RGBMatrixEmulator import graphics
        else:
            from rgbmatrix import graphics

        icon_width = self._get_icon_width()
        start_x, start_y = self._calculate_start_position()

        # Get the active color based on current crowding level
        active_color = self._get_active_color()

        # Render each of the 5 icons
        for i in range(5):
            # Icon index is 1-based for comparison with value
            icon_index = i + 1

            # Determine color based on whether this icon should be active
            if icon_index <= self._value:
                color = active_color
            else:
                color = self.inactive_color

            # Calculate x position for this icon
            x_pos = start_x + (i * (icon_width + self.spacing))

            # Create graphics color and draw the icon
            gfx_color = graphics.Color(*color.as_tuple())
            graphics.DrawText(
                canvas, self.font, x_pos, start_y, gfx_color, self.ICON_CHAR
            )

        self._needs_redraw = False
        self._dirty = False

    def _get_component_pixels(
        self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]
    ) -> None:
        """Get pixels for crowding icon rendering."""
        if not self.font:
            return

        icon_width = self._get_icon_width()
        start_x, start_y = self._calculate_start_position()
        baseline = self._get_font_baseline()
        font_height = self.font.height if hasattr(self.font, "height") else 8

        # Get the active color based on current crowding level
        active_color = self._get_active_color()

        # For testing/preview, add placeholder pixels for each icon position
        for i in range(5):
            icon_index = i + 1

            if icon_index <= self._value:
                color = active_color.as_tuple()
            else:
                color = self.inactive_color.as_tuple()

            x_pos = start_x + (i * (icon_width + self.spacing))
            # Approximate icon area
            for dx in range(icon_width):
                for dy in range(font_height):
                    px = x_pos + dx
                    py = start_y - baseline + dy
                    if self.region.contains(Position(px, py)):
                        pixels.append((px, py, color))

    def is_dirty(self) -> bool:
        """Check if component needs redrawing."""
        return self._needs_redraw or self._dirty
