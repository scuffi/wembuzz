"""Shape components for drawing rectangles, lines, and pixels."""

from typing import Optional, List, Tuple
from ..utils import Position, Color, Region
from .base import Component


class RectangleComponent(Component):
    """Component for drawing filled or outlined rectangles."""

    def __init__(
        self,
        region: Region,
        color: Color = Color(255, 255, 255),
        fill: bool = True,
        border_width: int = 1,
        border_color: Optional[Color] = None,
        background_color: Optional[Color] = None,
        visible: bool = True
    ):
        """
        Initialize a rectangle component.

        Args:
            region: The region this component occupies
            color: Fill color (if fill=True) or border color (if fill=False)
            fill: Whether to fill the rectangle
            border_width: Width of the border (if fill=False or border_color specified)
            border_color: Optional border color (if None, uses color)
            background_color: Optional background color
            visible: Whether the component is visible
        """
        super().__init__(region, background_color, visible)
        self.color = color
        self.fill = fill
        self.border_width = border_width
        self.border_color = border_color or color

    def render(self, canvas) -> None:
        """Render rectangle to the canvas."""
        if not self.visible:
            return

        # Draw background if specified
        if self.background_color:
            bg = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, bg[0], bg[1], bg[2])

        if self.fill:
            # Fill rectangle
            fill_color = self.color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, fill_color[0], fill_color[1], fill_color[2])

            # Draw border if different color
            if self.border_color != self.color:
                self._draw_border(canvas)
        else:
            # Draw border only
            self._draw_border(canvas)

    def _draw_border(self, canvas) -> None:
        """Draw rectangle border."""
        border_color = self.border_color.as_tuple()

        # Top and bottom borders
        for x in range(self.region.x, self.region.x + self.region.width):
            for w in range(self.border_width):
                # Top border
                if self.region.y + w < self.region.y + self.region.height:
                    canvas.SetPixel(x, self.region.y + w, border_color[0], border_color[1], border_color[2])
                # Bottom border
                if self.region.y + self.region.height - 1 - w >= self.region.y:
                    canvas.SetPixel(x, self.region.y + self.region.height - 1 - w, border_color[0], border_color[1], border_color[2])

        # Left and right borders
        for y in range(self.region.y, self.region.y + self.region.height):
            for w in range(self.border_width):
                # Left border
                if self.region.x + w < self.region.x + self.region.width:
                    canvas.SetPixel(self.region.x + w, y, border_color[0], border_color[1], border_color[2])
                # Right border
                if self.region.x + self.region.width - 1 - w >= self.region.x:
                    canvas.SetPixel(self.region.x + self.region.width - 1 - w, y, border_color[0], border_color[1], border_color[2])

    def _get_component_pixels(self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
        """Get pixels for rectangle rendering."""
        if self.fill:
            fill_color = self.color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    pixels.append((x, y, fill_color))

        # Add border pixels if needed
        if not self.fill or self.border_color != self.color:
            border_color = self.border_color.as_tuple()
            # Top
            for x in range(self.region.x, self.region.x + self.region.width):
                for w in range(self.border_width):
                    if self.region.y + w < self.region.y + self.region.height:
                        pixels.append((x, self.region.y + w, border_color))
            # Bottom
            for x in range(self.region.x, self.region.x + self.region.width):
                for w in range(self.border_width):
                    y = self.region.y + self.region.height - 1 - w
                    if y >= self.region.y:
                        pixels.append((x, y, border_color))
            # Left
            for y in range(self.region.y, self.region.y + self.region.height):
                for w in range(self.border_width):
                    if self.region.x + w < self.region.x + self.region.width:
                        pixels.append((self.region.x + w, y, border_color))
            # Right
            for y in range(self.region.y, self.region.y + self.region.height):
                for w in range(self.border_width):
                    x = self.region.x + self.region.width - 1 - w
                    if x >= self.region.x:
                        pixels.append((x, y, border_color))

    def set_color(self, color: Color) -> None:
        """Update fill/border color."""
        if self.color != color:
            self.color = color
            self.mark_dirty()

    def set_fill(self, fill: bool) -> None:
        """Update fill mode."""
        if self.fill != fill:
            self.fill = fill
            self.mark_dirty()


class LineComponent(Component):
    """Component for drawing lines."""

    def __init__(
        self,
        start: Position,
        end: Position,
        color: Color = Color(255, 255, 255),
        width: int = 1,
        background_color: Optional[Color] = None,
        visible: bool = True
    ):
        """
        Initialize a line component.

        Args:
            start: Start position
            end: End position
            color: Line color
            width: Line width in pixels
            background_color: Optional background color
            visible: Whether the component is visible
        """
        # Calculate bounding region
        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        min_y = min(start.y, end.y)
        max_y = max(start.y, end.y)
        region = Region(min_x, min_y, max_x - min_x + width, max_y - min_y + width)

        super().__init__(region, background_color, visible)
        self.start = start
        self.end = end
        self.color = color
        self.width = width

    def render(self, canvas) -> None:
        """Render line to the canvas."""
        if not self.visible:
            return

        # Draw background if specified
        if self.background_color:
            bg = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, bg[0], bg[1], bg[2])

        # Draw line using Bresenham's algorithm
        color = self.color.as_tuple()
        self._draw_line(canvas, self.start, self.end, color, self.width)

    def _draw_line(self, canvas, start: Position, end: Position, color: Tuple[int, int, int], width: int) -> None:
        """Draw a line using Bresenham's algorithm."""
        x0, y0 = start.x, start.y
        x1, y1 = end.x, end.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            # Draw pixel with width
            for w in range(width):
                for h in range(width):
                    px = x + w - width // 2
                    py = y + h - width // 2
                    if self.region.contains(Position(px, py)):
                        canvas.SetPixel(px, py, color[0], color[1], color[2])

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _get_component_pixels(self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
        """Get pixels for line rendering."""
        color = self.color.as_tuple()
        x0, y0 = self.start.x, self.start.y
        x1, y1 = self.end.x, self.end.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            for w in range(self.width):
                for h in range(self.width):
                    px = x + w - self.width // 2
                    py = y + h - self.width // 2
                    if self.region.contains(Position(px, py)):
                        pixels.append((px, py, color))

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def set_color(self, color: Color) -> None:
        """Update line color."""
        if self.color != color:
            self.color = color
            self.mark_dirty()

    def set_points(self, start: Position, end: Position) -> None:
        """Update line endpoints."""
        if self.start != start or self.end != end:
            self.start = start
            self.end = end
            # Recalculate region
            min_x = min(start.x, end.x)
            max_x = max(start.x, end.x)
            min_y = min(start.y, end.y)
            max_y = max(start.y, end.y)
            self.region = Region(min_x, min_y, max_x - min_x + self.width, max_y - min_y + self.width)
            self.mark_dirty()


class PixelComponent(Component):
    """Component for custom pixel-by-pixel drawing."""

    def __init__(
        self,
        region: Region,
        pixel_data: Optional[List[Tuple[int, int, Color]]] = None,
        background_color: Optional[Color] = None,
        visible: bool = True
    ):
        """
        Initialize a pixel component.

        Args:
            region: The region this component occupies
            pixel_data: List of (x, y, Color) tuples relative to region
            background_color: Optional background color
            visible: Whether the component is visible
        """
        super().__init__(region, background_color, visible)
        self.pixel_data = pixel_data or []

    def render(self, canvas) -> None:
        """Render pixels to the canvas."""
        if not self.visible:
            return

        # Draw background if specified
        if self.background_color:
            bg = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, bg[0], bg[1], bg[2])

        # Draw custom pixels
        for rel_x, rel_y, pixel_color in self.pixel_data:
            abs_x = self.region.x + rel_x
            abs_y = self.region.y + rel_y
            if self.region.contains(Position(abs_x, abs_y)):
                rgb = pixel_color.as_tuple()
                canvas.SetPixel(abs_x, abs_y, rgb[0], rgb[1], rgb[2])

    def _get_component_pixels(self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
        """Get pixels for custom pixel rendering."""
        for rel_x, rel_y, pixel_color in self.pixel_data:
            abs_x = self.region.x + rel_x
            abs_y = self.region.y + rel_y
            if self.region.contains(Position(abs_x, abs_y)):
                pixels.append((abs_x, abs_y, pixel_color.as_tuple()))

    def set_pixel(self, rel_x: int, rel_y: int, color: Color) -> None:
        """Set a pixel at relative position."""
        # Remove existing pixel at this position if any
        self.pixel_data = [(x, y, c) for x, y, c in self.pixel_data if not (x == rel_x and y == rel_y)]
        self.pixel_data.append((rel_x, rel_y, color))
        self.mark_dirty()

    def clear_pixels(self) -> None:
        """Clear all custom pixels."""
        self.pixel_data = []
        self.mark_dirty()

    def set_pixels(self, pixel_data: List[Tuple[int, int, Color]]) -> None:
        """Set all pixels at once."""
        self.pixel_data = pixel_data
        self.mark_dirty()


class BorderComponent(Component):
    """Component for animated border with rotating rainbow gradient dashes."""

    def __init__(
        self,
        region: Region,
        num_dashes: int = 8,
        dash_length: int = 4,
        dash_gap: int = 2,
        speed: float = 1.0,
        background_color: Optional[Color] = None,
        visible: bool = True
    ):
        """
        Initialize an animated border component.

        Args:
            region: The region this component occupies (defines the border)
            num_dashes: Number of dashes around the border
            dash_length: Length of each dash in pixels
            dash_gap: Gap between dashes in pixels
            speed: Animation speed multiplier (1.0 = normal speed)
            background_color: Optional background color
            visible: Whether the component is visible
        """
        super().__init__(region, background_color, visible)
        self.num_dashes = num_dashes
        self.dash_length = dash_length
        self.dash_gap = dash_gap
        self.speed = speed
        self._frame = 0

        # Calculate border perimeter
        self._border_positions = self._calculate_border_positions()

    def is_dirty(self) -> bool:
        """Always return True for animated border to ensure continuous rendering."""
        return True

    def _calculate_border_positions(self) -> List[Tuple[int, int]]:
        """Calculate all pixel positions along the border perimeter."""
        positions = []
        x, y = self.region.x, self.region.y
        w, h = self.region.width, self.region.height

        # Top edge (left to right)
        for i in range(w):
            positions.append((x + i, y))

        # Right edge (top to bottom, excluding corners)
        for i in range(1, h):
            positions.append((x + w - 1, y + i))

        # Bottom edge (right to left, excluding corners)
        for i in range(w - 2, -1, -1):
            positions.append((x + i, y + h - 1))

        # Left edge (bottom to top, excluding corners)
        for i in range(h - 2, 0, -1):
            positions.append((x, y + i))

        return positions

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB color."""
        import math
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c

        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return (
            int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255)
        )

    def _get_rainbow_color(self, position: float) -> Color:
        """Get rainbow color at position (0.0 to 1.0)."""
        # Use HSV color space for smooth rainbow gradient
        # Position wraps around for continuous gradient
        hue = (position % 1.0)
        rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
        return Color(rgb[0], rgb[1], rgb[2])

    def render(self, canvas) -> None:
        """Render animated border to the canvas."""
        if not self.visible:
            return

        # Draw background if specified
        if self.background_color:
            bg = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, bg[0], bg[1], bg[2])

        if not self._border_positions:
            return

        # Clear all border pixels first (set to black) to remove previous frame's dashes
        # This is necessary for animation since dashes move around
        for x, y in self._border_positions:
            canvas.SetPixel(x, y, 0, 0, 0)

        # Calculate total perimeter length
        perimeter_length = len(self._border_positions)

        # Increment frame counter for animation
        self._frame += 1

        # Calculate animation offset based on frame
        # Speed controls how fast it rotates
        offset = (self._frame * self.speed) % perimeter_length

        # Calculate gradient offset based on frame to make gradient rotate with dashes
        # This creates a smooth color shift as the dashes move around the border
        gradient_offset = (self._frame * self.speed) / perimeter_length

        # Draw dashes around the border
        for dash_idx in range(self.num_dashes):
            # Calculate starting position for this dash
            dash_start = (int(offset) + dash_idx * (perimeter_length // self.num_dashes)) % perimeter_length

            # Draw each pixel in the dash
            for i in range(self.dash_length):
                pos_idx = (dash_start + i) % perimeter_length
                if pos_idx < len(self._border_positions):
                    x, y = self._border_positions[pos_idx]

                    # Calculate color position for gradient effect
                    # Base color based on dash position around the border
                    # Add gradient offset so colors shift as dashes move
                    # Each dash gets a different hue, and pixels within dash have slight variation
                    base_color_pos = (dash_idx / self.num_dashes + i / (self.dash_length * self.num_dashes)) % 1.0
                    dash_color_pos = (base_color_pos + gradient_offset) % 1.0
                    color = self._get_rainbow_color(dash_color_pos)
                    rgb = color.as_tuple()
                    canvas.SetPixel(x, y, rgb[0], rgb[1], rgb[2])

    def _get_component_pixels(self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
        """Get pixels for border rendering (snapshot at current frame)."""
        if not self._border_positions:
            return

        perimeter_length = len(self._border_positions)
        offset = (self._frame * self.speed) % perimeter_length

        # Calculate gradient offset based on frame to make gradient rotate with dashes
        gradient_offset = (self._frame * self.speed) / perimeter_length

        for dash_idx in range(self.num_dashes):
            dash_start = (int(offset) + dash_idx * (perimeter_length // self.num_dashes)) % perimeter_length

            for i in range(self.dash_length):
                pos_idx = (dash_start + i) % perimeter_length
                if pos_idx < len(self._border_positions):
                    x, y = self._border_positions[pos_idx]
                    # Include gradient offset in color calculation
                    base_color_pos = (dash_idx / self.num_dashes + i / (self.dash_length * self.num_dashes)) % 1.0
                    dash_color_pos = (base_color_pos + gradient_offset) % 1.0
                    color = self._get_rainbow_color(dash_color_pos)
                    pixels.append((x, y, color.as_tuple()))

    def set_num_dashes(self, num_dashes: int) -> None:
        """Update number of dashes."""
        if self.num_dashes != num_dashes:
            self.num_dashes = num_dashes
            self.mark_dirty()

    def set_dash_length(self, dash_length: int) -> None:
        """Update dash length."""
        if self.dash_length != dash_length:
            self.dash_length = dash_length
            self.mark_dirty()

    def set_dash_gap(self, dash_gap: int) -> None:
        """Update dash gap."""
        if self.dash_gap != dash_gap:
            self.dash_gap = dash_gap
            self.mark_dirty()

    def set_speed(self, speed: float) -> None:
        """Update animation speed."""
        if self.speed != speed:
            self.speed = speed
            self.mark_dirty()

    def reset_animation(self) -> None:
        """Reset animation to frame 0."""
        self._frame = 0
        self.mark_dirty()
