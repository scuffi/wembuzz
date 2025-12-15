"""Text component for displaying text on the LED matrix."""

import threading
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
        max_text_length: Optional[int] = None,
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
            max_text_length: Optional maximum text length. If specified, text will be
                trimmed to this length and '...' will be appended if truncated.
        """
        super().__init__(region, background_color, visible)
        self.max_text_length = max_text_length
        self.text = self._trim_text(text) if max_text_length is not None else text
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

        # Caching to avoid unnecessary rerenders
        self._last_rendered_text = ""
        self._last_rendered_color = None
        self._last_rendered_progress = -1.0
        self._needs_clear = True  # Only clear when text actually changes

        # Animation timer for self-updating animations
        self._animation_timer: Optional[threading.Timer] = None
        self._animation_frame_duration = 0.033  # ~30 FPS for animations

    def _trim_text(self, text: str) -> str:
        """
        Trim text to max_text_length and append '...' if truncated.

        Args:
            text: The text to trim

        Returns:
            Trimmed text with '...' appended if it was truncated
        """
        if self.max_text_length is None or len(text) <= self.max_text_length:
            return text
        return text[: self.max_text_length] + "..."

    def render(self, canvas) -> None:
        """Render text to the canvas."""
        if not self.visible:
            return

        # Don't update animation here - it's handled by timer
        # Just render the current animation state
        if self._is_animating:
            # Always render during animation - position/opacity changes every frame
            # Clear region every frame during animation for smooth movement
            clear_color = (
                self.background_color.as_tuple() if self.background_color else (0, 0, 0)
            )
            for y in range(self.region.y, self.region.y + self.region.height):
                for x in range(self.region.x, self.region.x + self.region.width):
                    canvas.SetPixel(
                        x, y, clear_color[0], clear_color[1], clear_color[2]
                    )
            self._render_animated(canvas)
            self._last_rendered_progress = self._animation_progress
            return

        # For static text, always render to maintain display state
        # SwapOnVSync gives us a fresh back buffer, so we need to redraw everything
        # Always clear the region first (we're drawing to a fresh buffer)
        clear_color = (
            self.background_color.as_tuple() if self.background_color else (0, 0, 0)
        )
        for y in range(self.region.y, self.region.y + self.region.height):
            for x in range(self.region.x, self.region.x + self.region.width):
                canvas.SetPixel(x, y, clear_color[0], clear_color[1], clear_color[2])

        # Always render static text (to maintain state after canvas swap)
        self._render_static(canvas)

        # Update cache and reset flags
        self._last_rendered_text = self.text
        self._last_rendered_color = self.color
        self._last_rendered_progress = -1.0
        self._needs_clear = False
        self._dirty = False  # Mark clean since we just rendered

    def _render_static(self, canvas) -> None:
        """Render static text (no animation)."""
        # If text is empty, region was already cleared in render(), so we're done
        if not self.text:
            return

        if not self.font:
            return

        # No need to clear here - already cleared in render() if needed
        import os

        if os.environ.get("LED_ENV") == "emulator":
            from RGBMatrixEmulator import graphics
        else:
            from rgbmatrix import graphics

        text_x, text_y = self._calculate_text_position()
        color = graphics.Color(*self.color.as_tuple())
        graphics.DrawText(canvas, self.font, text_x, text_y, color, str(self.text))

    def _render_animated(self, canvas) -> None:
        """Render animated text based on animation type."""
        # Region already cleared in render() if needed
        # No need to clear every frame during animation - just update the animation frame

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
            font_height = (
                self.font.height if (self.font and hasattr(self.font, "height")) else 8
            )
            slide_distance = max(self.region.height, font_height)
            new_offset_x = 0
            old_offset_x = 0
            new_offset_y = int(-(1 - progress) * slide_distance)
            old_offset_y = int(progress * slide_distance)
        elif self._animation_type == AnimationType.SLIDE_DOWN:
            # New text slides in from top, old text slides out to bottom
            # Use font height for smoother animation even with small regions
            font_height = (
                self.font.height if (self.font and hasattr(self.font, "height")) else 8
            )
            slide_distance = max(self.region.height, font_height)
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

    def _get_font_baseline(self) -> int:
        """
        Get font baseline offset, compatible with both emulator and real rgbmatrix.
        Returns the baseline offset needed for proper text positioning.
        """
        if not self.font:
            return 0

        # Try to use baseline property if available (emulator has this)
        if hasattr(self.font, "baseline"):
            return self.font.baseline

        # Try to use headers if available (emulator)
        if hasattr(self.font, "headers"):
            return self.font.headers.get("fbby", 0) + self.font.headers.get(
                "fbbyoff", 0
            )

        # Fallback: use font height as baseline approximation
        # This works for most fonts where baseline is roughly at the bottom
        # Fallback: use font height as baseline approximation
        # This works for most fonts where baseline is roughly at the bottom
        if hasattr(self.font, "height"):
            return self.font.height

        # Last resort: assume baseline is same as height (common for bitmap fonts)
        return 8  # Default fallback

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
        baseline = self._get_font_baseline()

        if self.vertical_align == "top":
            text_y = self.region.y + baseline
        elif self.vertical_align == "center":
            font_height = self.font.height if hasattr(self.font, "height") else 8
            text_y = self.region.y + (self.region.height - font_height) // 2 + baseline
        elif self.vertical_align == "bottom":
            font_height = self.font.height if hasattr(self.font, "height") else 8
            text_y = self.region.y + self.region.height - font_height + baseline

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

        baseline = self._get_font_baseline()
        text_height = self.font.height if hasattr(self.font, "height") else 8

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

                font_y_offset = -self._get_font_baseline()
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
        """Update animation progress. Called by animation timer."""
        if not self._is_animating:
            return

        self._animation_progress += 1.0 / self._animation_duration

        if self._animation_progress >= 1.0:
            # Animation complete
            self._animation_progress = 1.0
            self.text = self._new_text
            self._is_animating = False
            self._animation_type = AnimationType.NONE
            # Stop animation timer
            if self._animation_timer:
                self._animation_timer.cancel()
                self._animation_timer = None
            # Reset cache and mark for rerender of final static state
            self._last_rendered_text = ""
            self._needs_clear = True
            # Sync screen to show final state
            self._sync()
        else:
            # Sync screen for this animation frame (shows current progress)
            self._sync()
            # Schedule next animation frame
            self._schedule_next_animation_frame()

    def is_animating(self) -> bool:
        """Check if text is currently animating."""
        return self._is_animating

    def is_dirty(self) -> bool:
        """Return True if animating or if needs to be rendered."""
        # During animation, always consider dirty (position/opacity changes every frame)
        if self._is_animating:
            return True
        # For static text, only dirty if _needs_clear is True (set by set_text/set_color)
        # Ignore the _dirty flag for static text to prevent unnecessary rerenders
        return self._needs_clear

    def _schedule_next_animation_frame(self) -> None:
        """Schedule the next animation frame update."""
        if not self._is_animating:
            return

        # Cancel existing timer if any
        if self._animation_timer:
            self._animation_timer.cancel()

        # Schedule next frame
        self._animation_timer = threading.Timer(
            self._animation_frame_duration, self.update_animation
        )
        self._animation_timer.daemon = True
        self._animation_timer.start()

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
        # Apply trimming if max_text_length is set
        trimmed_text = (
            self._trim_text(text) if self.max_text_length is not None else text
        )

        if self.text == trimmed_text and not self._is_animating:
            return

        # Stop any existing animation
        if self._animation_timer:
            self._animation_timer.cancel()
            self._animation_timer = None

        if animation is None or animation == AnimationType.NONE:
            # Instant change
            self.text = trimmed_text
            self._is_animating = False
            self._animation_type = AnimationType.NONE
            # Mark that we need to clear and rerender
            # This is the ONLY way static text gets marked for rendering
            self._needs_clear = True
            self._last_rendered_text = ""  # Force rerender
            # Sync screen immediately for static text change
            self._sync()
        else:
            # Start animation
            self._old_text = self.text
            self._new_text = trimmed_text
            self._animation_type = animation
            self._animation_progress = 0.0
            self._animation_duration = duration
            self._is_animating = True
            # Mark that we need to clear at the start of animation
            self._needs_clear = True
            self._last_rendered_progress = -1.0  # Reset progress cache
            # Render first frame immediately, then start animation timer
            self._sync()
            self._schedule_next_animation_frame()

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
            char_height = self.font.height if hasattr(self.font, "height") else 8
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
            self._last_rendered_color = None  # Force rerender
            # Mark that we need to clear and rerender
            # This is the ONLY way static text gets marked for rendering
            self._needs_clear = True
            # Sync screen immediately
            self._sync()

    def set_align(self, align: str) -> None:
        """Update horizontal alignment."""
        if self.align != align:
            self.align = align
            # Mark that we need to clear and rerender
            self._needs_clear = True
            # Don't call mark_dirty() - we use _needs_clear for static text

    def set_vertical_align(self, vertical_align: str) -> None:
        """Update vertical alignment."""
        if self.vertical_align != vertical_align:
            self.vertical_align = vertical_align
            # Mark that we need to clear and rerender
            self._needs_clear = True
            # Sync screen immediately
            self._sync()
