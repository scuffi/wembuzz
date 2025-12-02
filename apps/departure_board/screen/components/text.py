"""Text component for displaying text on the LED matrix."""

from typing import Optional
from enum import Enum
from ..utils import Position, Color, Region
from .base import Component


class AnimationType(Enum):
    """Types of text animations."""

    NONE = "none"
    PUSH = "push"  # Old text pushes out, new text pushes in
    FADE = "fade"  # Fade in new text
    TYPEWRITER = "typewriter"  # Characters appear one by one
    SLIDE_LEFT = "slide_left"  # Slide in from right
    SLIDE_RIGHT = "slide_right"  # Slide in from left
    SLIDE_UP = "slide_up"  # Slide in from bottom
    SLIDE_DOWN = "slide_down"  # Slide in from top


class TextComponent(Component):
    """Component for displaying text."""

    def __init__(
        self,
        region: Region,
        text: str = "",
        font=None,
        color: Color = Color(255, 255, 255),
        background_color: Optional[Color] = None,
        align: str = "left",  # "left", "center", "right"
        vertical_align: str = "top",  # "top", "center", "bottom"
        visible: bool = True,
    ):
        """
        Initialize a text component.

        Args:
            region: The region this component occupies
            text: The text to display
            font: Font object (from rgbmatrix.graphics.Font or similar)
            color: Text color
            background_color: Optional background color
            align: Horizontal alignment ("left", "center", "right")
            vertical_align: Vertical alignment ("top", "center", "bottom")
            visible: Whether the component is visible
        """
        super().__init__(region, background_color, visible)
        self.text = text
        self.font = font
        self.color = color
        self.align = align
        self.vertical_align = vertical_align

        # Animation state
        self._animation_type = AnimationType.NONE
        self._animation_progress = 0.0  # 0.0 to 1.0
        self._animation_duration = 30  # frames
        self._old_text = ""
        self._new_text = ""
        self._is_animating = False

    def render(self, canvas) -> None:
        """Render text to the canvas."""
        if not self.visible:
            return

        # Draw background if specified
        if self.background_color:
            bg = self.background_color.as_tuple()
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, bg[0], bg[1], bg[2])

        # Update animation if in progress
        if self._is_animating:
            self.update_animation()

        # Render based on animation state
        if self._is_animating:
            self._render_animated(canvas)
        else:
            self._render_static(canvas)

    def _render_static(self, canvas) -> None:
        """Render static text (no animation)."""
        if not self.text:
            # Clear region if text is empty
            if not self.background_color:
                for y in range(self.region.y, self.region.y + self.region.height):
                    for x in range(self.region.x, self.region.x + self.region.width):
                        canvas.SetPixel(x, y, 0, 0, 0)
            return

        if not self.font:
            return

        # Clear the region first to remove old text pixels
        # This is needed when text is updated without animation
        # Background color is already drawn in render(), so only clear if no background
        if not self.background_color:
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(x, y, 0, 0, 0)

        import os

        if os.environ.get("LED_ENV") == "emulator":
            from RGBMatrixEmulator import graphics
        else:
            from rgbmatrix import graphics

        text_x, text_y = self._calculate_text_position()
        color = graphics.Color(*self.color.as_tuple())
        graphics.DrawText(canvas, self.font, text_x, text_y, color, self.text)

    def _render_animated(self, canvas) -> None:
        """Render animated text based on animation type."""
        # Clear the region first to remove old text pixels
        # This prevents accumulation of pixels during animation
        clear_color = (
            self.background_color.as_tuple() if self.background_color else (0, 0, 0)
        )
        for y in range(self.region.y, self.region.y + self.region.height):
            for x in range(self.region.x, self.region.x + self.region.width):
                canvas.SetPixel(x, y, clear_color[0], clear_color[1], clear_color[2])

        import os

        if os.environ.get("LED_ENV") == "emulator":
            from RGBMatrixEmulator import graphics
        else:
            from rgbmatrix import graphics

        progress = self._animation_progress

        if self._animation_type == AnimationType.PUSH:
            self._render_push_animation(canvas, graphics, progress)
        elif self._animation_type == AnimationType.FADE:
            self._render_fade_animation(canvas, graphics, progress)
        elif self._animation_type == AnimationType.TYPEWRITER:
            self._render_typewriter_animation(canvas, graphics, progress)
        elif self._animation_type in [
            AnimationType.SLIDE_LEFT,
            AnimationType.SLIDE_RIGHT,
            AnimationType.SLIDE_UP,
            AnimationType.SLIDE_DOWN,
        ]:
            self._render_slide_animation(canvas, graphics, progress)
        else:
            # Fallback to static
            self._render_static(canvas)

    def _render_push_animation(self, canvas, graphics, progress: float) -> None:
        """Render push animation: old text pushes out, new text pushes in."""
        if not self.font:
            return

        # Calculate new text width for positioning
        new_width = (
            sum(self.font.CharacterWidth(ord(c)) for c in self._new_text)
            if self._new_text
            else 0
        )

        # Get base positions
        base_x_old, text_y = self._calculate_text_position_for_text(self._old_text)
        base_x_new, _ = self._calculate_text_position_for_text(self._new_text)

        # Old text moves out (left if left-aligned, right if right-aligned)
        if self.align == "right":
            old_offset = int((1 - progress) * self.region.width)
            old_x = base_x_old + old_offset
        else:  # left or center
            old_offset = int(-progress * self.region.width)
            old_x = base_x_old + old_offset

        # New text moves in from opposite direction
        if self.align == "right":
            new_offset = int(progress * self.region.width)
            new_x = base_x_new - new_width + new_offset
        else:  # left or center
            new_offset = int((1 - progress) * self.region.width)
            new_x = base_x_new - new_offset

        # Draw old text (fading out)
        if self._old_text and progress < 0.8:
            old_alpha = 1.0 - (progress / 0.8)
            old_color = self._apply_alpha(self.color, old_alpha)
            self._draw_text_clipped(
                canvas, graphics, old_x, text_y, old_color, self._old_text
            )

        # Draw new text (fading in)
        if self._new_text and progress > 0.2:
            new_alpha = min(1.0, (progress - 0.2) / 0.8)
            new_color = self._apply_alpha(self.color, new_alpha)
            self._draw_text_clipped(
                canvas, graphics, new_x, text_y, new_color, self._new_text
            )

    def _render_fade_animation(self, canvas, graphics, progress: float) -> None:
        """Render fade in animation."""
        if not self.font or not self._new_text:
            return

        text_x, text_y = self._calculate_text_position_for_text(self._new_text)

        # Fade in new text
        fade_color = self._apply_alpha(self.color, progress)
        self._draw_text_clipped(
            canvas, graphics, text_x, text_y, fade_color, self._new_text
        )

    def _render_typewriter_animation(self, canvas, graphics, progress: float) -> None:
        """Render typewriter animation: characters appear one by one."""
        if not self.font or not self._new_text:
            return

        # Calculate how many characters to show
        num_chars = int(len(self._new_text) * progress)
        display_text = self._new_text[:num_chars]

        if display_text:
            text_x, text_y = self._calculate_text_position_for_text(display_text)
            self._draw_text_clipped(
                canvas, graphics, text_x, text_y, self.color, display_text
            )

    def _render_slide_animation(self, canvas, graphics, progress: float) -> None:
        """Render slide animation: new text pushes old text out (like departure board)."""
        if not self.font:
            return

        # Get base positions for both texts
        base_x_old, text_y = self._calculate_text_position_for_text(self._old_text)
        base_x_new, _ = self._calculate_text_position_for_text(self._new_text)

        # Calculate offsets based on direction - old text moves out, new text moves in
        if self._animation_type == AnimationType.SLIDE_LEFT:
            # New text slides in from right, old text slides out to left
            new_offset_x = int((1 - progress) * self.region.width)
            old_offset_x = int(-progress * self.region.width)
            new_offset_y = 0
            old_offset_y = 0
        elif self._animation_type == AnimationType.SLIDE_RIGHT:
            # New text slides in from left, old text slides out to right
            new_offset_x = int(-(1 - progress) * self.region.width)
            old_offset_x = int(progress * self.region.width)
            new_offset_y = 0
            old_offset_y = 0
        elif self._animation_type == AnimationType.SLIDE_UP:
            # New text slides in from bottom, old text slides out to top
            # Use font height for smoother animation even with small regions
            slide_distance = max(
                self.region.height, self.font.height if self.font else 8
            )
            new_offset_x = 0
            old_offset_x = 0
            new_offset_y = int(-(1 - progress) * slide_distance)
            old_offset_y = int(progress * slide_distance)
        elif self._animation_type == AnimationType.SLIDE_DOWN:
            # New text slides in from top, old text slides out to bottom
            # Use font height for smoother animation even with small regions
            slide_distance = max(
                self.region.height, self.font.height if self.font else 8
            )
            new_offset_x = 0
            old_offset_x = 0
            new_offset_y = int((1 - progress) * slide_distance)
            old_offset_y = int(-progress * slide_distance)
        else:
            new_offset_x = 0
            old_offset_x = 0
            new_offset_y = 0
            old_offset_y = 0

        # Calculate final positions
        if self._animation_type in [
            AnimationType.SLIDE_LEFT,
            AnimationType.SLIDE_RIGHT,
        ]:
            old_x = base_x_old + old_offset_x
            new_x = base_x_new + new_offset_x
            old_y = text_y
            new_y = text_y
        else:  # SLIDE_UP or SLIDE_DOWN
            old_x = base_x_old
            new_x = base_x_new
            old_y = text_y + old_offset_y
            new_y = text_y + new_offset_y

        # Draw old text being pushed out (fade out as it exits)
        if self._old_text and progress < 0.9:
            old_alpha = 1.0 - (progress / 0.9)
            old_color = self._apply_alpha(self.color, old_alpha)
            self._draw_text_clipped(
                canvas, graphics, old_x, old_y, old_color, self._old_text
            )

        # Draw new text sliding in (fade in as it enters)
        if self._new_text and progress > 0.1:
            new_alpha = min(1.0, (progress - 0.1) / 0.9)
            new_color = self._apply_alpha(self.color, new_alpha)
            self._draw_text_clipped(
                canvas, graphics, new_x, new_y, new_color, self._new_text
            )

    def _calculate_text_position(self) -> tuple:
        """Calculate text position based on alignment (uses current text)."""
        display_text = self._new_text if self._is_animating else self.text
        return self._calculate_text_position_for_text(display_text)

    def _calculate_text_position_for_text(self, text: str) -> tuple:
        """Calculate text position for a specific text string."""
        if not self.font or not text:
            return (self.region.x, self.region.y)

        text_x = self.region.x
        text_y = self.region.y

        # Horizontal alignment
        if self.align == "center":
            text_width = sum(self.font.CharacterWidth(ord(c)) for c in text)
            text_x = self.region.x + (self.region.width - text_width) // 2
            if text_x < self.region.x:
                text_x = self.region.x
        elif self.align == "right":
            text_width = sum(self.font.CharacterWidth(ord(c)) for c in text)
            text_x = self.region.x + self.region.width - text_width
            if text_x < self.region.x:
                text_x = self.region.x
        else:  # "left"
            text_x = self.region.x

        # Vertical alignment
        baseline = self.font.headers.get("fbby", 0) + self.font.headers.get(
            "fbbyoff", 0
        )

        if self.vertical_align == "top":
            text_y = self.region.y + baseline
        elif self.vertical_align == "center":
            text_y = (
                self.region.y + (self.region.height - self.font.height) // 2 + baseline
            )
        elif self.vertical_align == "bottom":
            text_y = self.region.y + self.region.height - self.font.height + baseline

        return (text_x, text_y)

    def _apply_alpha(self, color: Color, alpha: float) -> Color:
        """Apply alpha transparency to a color (multiplies RGB by alpha)."""
        alpha = max(0.0, min(1.0, alpha))
        return Color(int(color.r * alpha), int(color.g * alpha), int(color.b * alpha))

    def _draw_text_clipped(
        self, canvas, graphics, x: int, y: int, color: Color, text: str
    ) -> None:
        """
        Draw text with strict clipping to region bounds.
        Only renders pixels that are within the component's region.
        Uses pixel-by-pixel rendering to ensure no pixels are drawn outside.
        """
        if not self.font or not text:
            return

        baseline = self.font.headers.get("fbby", 0) + self.font.headers.get(
            "fbbyoff", 0
        )
        text_height = self.font.height

        # Calculate actual text bounds (accounting for baseline)
        text_top = y - baseline
        text_bottom = text_top + text_height

        # Check if text is completely outside region
        text_width = sum(self.font.CharacterWidth(ord(c)) for c in text)
        if (
            x + text_width < self.region.x
            or x > self.region.x + self.region.width
            or text_bottom < self.region.y
            or text_top > self.region.y + self.region.height
        ):
            return  # Text is completely outside region

        # For text that might extend outside region, render pixel-by-pixel with clipping
        # This ensures NO pixels are drawn outside the region, but allows partial overlaps
        # Always use pixel-by-pixel rendering for proper clipping during animations
        try:
            # Get font bitmap data
            if hasattr(self.font, "bdf_font"):
                # Render text to get bitmap
                text_map = self.font.bdf_font.draw(
                    text,
                    len(text) * (text_width + 1),
                    missing=self.font.default_character,
                ).todata(2)

                font_y_offset = -(
                    self.font.headers["fbby"] + self.font.headers["fbbyoff"]
                )
                color_rgb = color.as_tuple()

                # Render each pixel with strict region checking
                for y2, row in enumerate(text_map):
                    for x2, value in enumerate(row):
                        if value == 1:  # Pixel is set
                            pixel_x = x + x2
                            pixel_y = y + y2 + font_y_offset

                            # STRICT clipping - only draw if pixel is within region
                            if (
                                pixel_x >= self.region.x
                                and pixel_x < self.region.x + self.region.width
                                and pixel_y >= self.region.y
                                and pixel_y < self.region.y + self.region.height
                            ):
                                canvas.SetPixel(
                                    pixel_x,
                                    pixel_y,
                                    color_rgb[0],
                                    color_rgb[1],
                                    color_rgb[2],
                                )
            else:
                # Fallback: use DrawText but only if text is fully within region
                # This is less ideal but better than nothing
                if (
                    x >= self.region.x
                    and x + text_width <= self.region.x + self.region.width
                    and text_top >= self.region.y
                    and text_bottom <= self.region.y + self.region.height
                ):
                    graphics.DrawText(
                        canvas, self.font, x, y, graphics.Color(*color.as_tuple()), text
                    )
        except Exception:
            # Fallback: render character-by-character, allowing partial overlaps
            # We'll use DrawText for each character and let it handle partial rendering
            # This is not perfect but better than not rendering at all
            current_x = x
            for char in text:
                char_width = self.font.CharacterWidth(ord(char))
                char_top = text_top
                char_bottom = text_bottom

                # Render if character overlaps with region (not just if fully within)
                if (
                    current_x + char_width >= self.region.x
                    and current_x < self.region.x + self.region.width
                    and char_bottom >= self.region.y
                    and char_top <= self.region.y + self.region.height
                ):
                    # Use DrawText - it will draw pixels, and we've already cleared the region
                    # This allows partial characters to be visible during animation
                    graphics.DrawText(
                        canvas,
                        self.font,
                        current_x,
                        y,
                        graphics.Color(*color.as_tuple()),
                        char,
                    )
                current_x += char_width

    def update_animation(self) -> None:
        """Update animation progress. Call this each frame during animation."""
        if not self._is_animating:
            return

        self._animation_progress += 1.0 / self._animation_duration

        if self._animation_progress >= 1.0:
            # Animation complete
            self._animation_progress = 1.0
            self.text = self._new_text
            self._is_animating = False
            self._animation_type = AnimationType.NONE

        self.mark_dirty()

    def is_animating(self) -> bool:
        """Check if text is currently animating."""
        return self._is_animating

    def is_dirty(self) -> bool:
        """Return True if animating or if dirty flag is set."""
        return self._is_animating or self._dirty

    def set_text(
        self, text: str, animation: Optional[AnimationType] = None, duration: int = 30
    ) -> None:
        """
        Update the text content with optional animation.

        Args:
            text: New text to display
            animation: Animation type (None = instant change)
            duration: Animation duration in frames
        """
        if self.text == text and not self._is_animating:
            return

        if animation is None or animation == AnimationType.NONE:
            # Instant change
            self.text = text
            self._is_animating = False
            self._animation_type = AnimationType.NONE
            self.mark_dirty()
        else:
            # Start animation
            self._old_text = self.text
            self._new_text = text
            self._animation_type = animation
            self._animation_progress = 0.0
            self._animation_duration = duration
            self._is_animating = True
            self.mark_dirty()

    def _draw_char_simple(self, canvas, char: str, x: int, y: int) -> None:
        """Simple character rendering (placeholder - very basic)."""
        # This is a minimal implementation
        # In production, you'd want a proper font bitmap
        color = self.color.as_tuple()
        # Just draw a few pixels to indicate text
        if (
            x < self.region.x + self.region.width
            and y < self.region.y + self.region.height
        ):
            canvas.SetPixel(x, y, color[0], color[1], color[2])

    def _get_component_pixels(self, pixels) -> None:
        """Get pixels for text rendering."""
        if not self.text:
            return

        color = self.color.as_tuple()
        # Simplified - in practice, you'd calculate actual text pixels
        # For now, just mark a few pixels
        if self.font:
            char_width = self.font.CharacterWidth(0) + 1
            char_height = self.font.height
        else:
            char_width = 4
            char_height = 6

        text_x = self.region.x
        text_y = self.region.y

        if self.align == "center":
            text_width = len(self.text) * char_width
            text_x = self.region.x + (self.region.width - text_width) // 2
        elif self.align == "right":
            text_width = len(self.text) * char_width
            text_x = self.region.x + self.region.width - text_width

        if self.vertical_align == "center":
            text_y = self.region.y + (self.region.height - char_height) // 2
        elif self.vertical_align == "bottom":
            text_y = self.region.y + self.region.height - char_height

        # Add placeholder pixels
        for i in range(len(self.text)):
            px = text_x + i * char_width
            py = text_y
            if self.region.contains(Position(px, py)):
                pixels.append((px, py, color))

    def set_color(self, color: Color) -> None:
        """Update text color."""
        if self.color != color:
            self.color = color
            self.mark_dirty()

    def set_align(self, align: str) -> None:
        """Update horizontal alignment."""
        if self.align != align:
            self.align = align
            self.mark_dirty()

    def set_vertical_align(self, vertical_align: str) -> None:
        """Update vertical alignment."""
        if self.vertical_align != vertical_align:
            self.vertical_align = vertical_align
            self.mark_dirty()
