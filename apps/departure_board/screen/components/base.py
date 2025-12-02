"""Base component class for all display components."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from ..utils import Position, Color, Region


class Component(ABC):
    """Base class for all display components."""

    def __init__(
        self,
        region: Region,
        background_color: Optional[Color] = None,
        visible: bool = True
    ):
        """
        Initialize a component.

        Args:
            region: The region this component occupies
            background_color: Optional background color (None = transparent)
            visible: Whether the component is visible
        """
        self.region = region
        self.background_color = background_color
        self.visible = visible
        self._dirty = True  # Track if component needs redrawing

    @abstractmethod
    def render(self, canvas) -> None:
        """
        Render this component to the canvas.

        Args:
            canvas: The RGBMatrix canvas to draw on
        """
        pass

    def get_pixels(self) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        """
        Get all pixels this component would render.
        Returns list of (x, y, (r, g, b)) tuples.

        This is useful for testing and previewing.
        """
        pixels = []
        if not self.visible:
            return pixels

        # Draw background if specified
        if self.background_color:
            bg_color = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    pixels.append((x, y, bg_color))

        # Let subclasses add their specific pixels
        self._get_component_pixels(pixels)
        return pixels

    @abstractmethod
    def _get_component_pixels(self, pixels: List[Tuple[int, int, Tuple[int, int, int]]]) -> None:
        """
        Add component-specific pixels to the list.

        Args:
            pixels: List to append (x, y, (r, g, b)) tuples to
        """
        pass

    def mark_dirty(self) -> None:
        """Mark this component as needing a redraw."""
        self._dirty = True

    def is_dirty(self) -> bool:
        """Check if component needs redrawing."""
        return self._dirty

    def mark_clean(self) -> None:
        """Mark this component as up-to-date."""
        self._dirty = False

    def set_visible(self, visible: bool) -> None:
        """Set component visibility."""
        if self.visible != visible:
            self.visible = visible
            self.mark_dirty()

    def set_region(self, region: Region) -> None:
        """Update component region."""
        if self.region != region:
            self.region = region
            self.mark_dirty()

    def set_background_color(self, color: Optional[Color]) -> None:
        """Update background color."""
        if self.background_color != color:
            self.background_color = color
            self.mark_dirty()
