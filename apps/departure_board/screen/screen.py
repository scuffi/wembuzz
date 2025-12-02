"""Main Screen/Display class for managing LED matrix display."""

import os

from typing import Dict, Optional, List
from .layouts.layout import Layout
from .components.base import Component
from .utils import Region, Color

# TODO: Support Conditional import for RGBMatrix
if os.environ.get("LED_ENV") == "emulator":
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics  # noqa: F401
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics  # noqa: F401

Font = graphics.Font


class Screen:
    """Main screen class for managing LED matrix display and components."""

    def __init__(
        self,
        width: int = 64,
        height: int = 32,
        hardware_mapping: str = "adafruit-hat",
        chain_length: int = 1,
        parallel: int = 1,
        pwm_bits: int = 11,
        brightness: int = 100,
        gpio_slowdown: int = 1,
        **kwargs,
    ):
        """
        Initialize the LED matrix screen.

        Args:
            width: Display width in pixels
            height: Display height in pixels
            hardware_mapping: Hardware mapping type
            chain_length: Number of chained displays
            parallel: Number of parallel chains
            pwm_bits: PWM bits
            brightness: Brightness (0-100)
            gpio_slowdown: GPIO slowdown factor
            **kwargs: Additional RGBMatrixOptions parameters
        """
        self.width = width
        self.height = height

        # Configure RGBMatrix options
        options = RGBMatrixOptions()
        options.hardware_mapping = hardware_mapping
        options.rows = height
        options.cols = width
        options.chain_length = chain_length
        options.parallel = parallel
        options.pwm_bits = pwm_bits
        options.brightness = brightness
        options.gpio_slowdown = gpio_slowdown

        # Apply any additional options
        for key, value in kwargs.items():
            if hasattr(options, key):
                setattr(options, key, value)

        # Create matrix
        self.matrix = RGBMatrix(options=options)
        self.canvas = self.matrix.CreateFrameCanvas()

        # Layout management
        self.layout: Optional[Layout] = None
        self.components: Dict[str, Component] = {}

        # Rendering state
        self._full_redraw = True

    def create_layout(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> Layout:
        """
        Create a new layout for organizing components.

        Args:
            width: Layout width (defaults to screen width)
            height: Layout height (defaults to screen height)

        Returns:
            The created layout
        """
        layout_width = width or self.width
        layout_height = height or self.height

        if layout_width > self.width or layout_height > self.height:
            raise ValueError(
                f"Layout size ({layout_width}x{layout_height}) exceeds screen size ({self.width}x{self.height})"
            )

        self.layout = Layout(layout_width, layout_height)

        # Define full screen region
        self.layout.define_region("full", Region(0, 0, layout_width, layout_height))

        return self.layout

    def add_component(
        self, name: str, component: Component, region_name: Optional[str] = None
    ) -> None:
        """
        Add a component to the screen.

        Args:
            name: Unique name for the component
            component: The component to add
            region_name: Optional layout region name to bind to
        """
        # Validate component fits on screen
        if component.region.x + component.region.width > self.width:
            raise ValueError(f"Component {name} extends beyond screen width")
        if component.region.y + component.region.height > self.height:
            raise ValueError(f"Component {name} extends beyond screen height")

        # If layout exists and region_name provided, bind to layout region
        if self.layout and region_name:
            self.layout.add_component(name, component, region_name)
        else:
            self.components[name] = component

        self._full_redraw = True

    def get_component(self, name: str) -> Optional[Component]:
        """Get a component by name."""
        if self.layout:
            component = self.layout.get_component(name)
            if component:
                return component
        return self.components.get(name)

    def remove_component(self, name: str) -> None:
        """Remove a component from the screen."""
        if self.layout:
            self.layout.remove_component(name)
        if name in self.components:
            del self.components[name]
        self._full_redraw = True

    def clear(self, color: Color = Color(0, 0, 0)) -> None:
        """Clear the entire screen with a color."""
        rgb = color.as_tuple()
        for y in range(self.height):
            for x in range(self.width):
                self.canvas.SetPixel(x, y, rgb[0], rgb[1], rgb[2])
        self._full_redraw = True

    def render(self, clear: bool = True, clear_color: Color = Color(0, 0, 0)) -> None:
        """
        Render all components to the display.

        Args:
            clear: Whether to clear the screen before rendering
            clear_color: Color to clear with
        """
        if clear or self._full_redraw:
            self.clear(clear_color)
            self._full_redraw = False

        # Collect all components
        all_components: List[Component] = []

        if self.layout:
            all_components.extend(self.layout.get_all_components().values())

        # Add standalone components (not in layout)
        for component in self.components.values():
            if component not in all_components:
                all_components.append(component)

        # Render only dirty components if not full redraw
        components_to_render = (
            all_components if clear else [c for c in all_components if c.is_dirty()]
        )

        # Render components
        for component in components_to_render:
            if component.visible:
                component.render(self.canvas)
                component.mark_clean()

        # Swap canvas
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def update(self) -> None:
        """Update the display (render and swap)."""
        self.render(clear=False)

    def set_brightness(self, brightness: int) -> None:
        """Set display brightness (0-100)."""
        self.matrix.brightness = max(0, min(100, brightness))

    def get_all_components(self) -> Dict[str, Component]:
        """Get all components on the screen."""
        all_components = {}

        if self.layout:
            all_components.update(self.layout.get_all_components())

        all_components.update(self.components)

        return all_components

    def mark_all_dirty(self) -> None:
        """Mark all components as needing redraw."""
        for component in self.get_all_components().values():
            component.mark_dirty()
        self._full_redraw = True
