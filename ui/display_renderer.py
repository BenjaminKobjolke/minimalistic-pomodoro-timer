"""Display rendering for the Pomodoro Timer application."""

import tkinter as tk
from typing import Optional
from PIL import Image, ImageFont, ImageDraw, ImageTk
from core.constants import (
    COLOR_TIMER_TEXT, COLOR_BACKGROUND, COLOR_BORDER_FOCUSED,
    WINDOW_PADDING_X, WINDOW_PADDING_Y,
    TEXT_OFFSET_X, TEXT_OFFSET_Y, TEXT_HEIGHT_ADJUSTMENT,
    DEFAULT_FONT_FILE, DEFAULT_FONT_SIZE
)
from logger import Logger


class DisplayRenderer:
    """Handles rendering of the timer display."""

    def __init__(self, window: tk.Tk, canvas: tk.Canvas):
        self.window = window
        self.canvas = canvas
        self.logger = Logger()
        self.font: Optional[ImageFont.FreeTypeFont] = None
        self.font_size = DEFAULT_FONT_SIZE
        self.width = 0
        self.height = 0
        self._time_image: Optional[ImageTk.PhotoImage] = None

    def load_font(self, font_path: Optional[str], font_size: int) -> None:
        """Load the font for display rendering."""
        self.font_size = font_size

        # Try to load custom font
        if font_path:
            try:
                self.font = ImageFont.truetype(font_path, self.font_size)
                self.logger.info(f"Custom font loaded: {font_path}")
                return
            except Exception as e:
                self.logger.warning(f"Could not load custom font: {e}")

        # Fallback to default font
        try:
            self.font = ImageFont.truetype(DEFAULT_FONT_FILE, self.font_size)
            self.logger.info("Using default Arial font")
        except Exception as e:
            self.logger.error(f"Could not load Arial font: {e}")
            raise SystemExit("Could not load any font. Please check your font configuration.")

    def calculate_dimensions(self) -> tuple[int, int]:
        """Calculate and return the window dimensions based on font size."""
        if not self.font:
            raise ValueError("Font must be loaded before calculating dimensions")

        # Create temporary image to measure text
        img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), "00:00", font=self.font)

        self.width = bbox[2] - bbox[0] + WINDOW_PADDING_X
        self.height = bbox[3] - bbox[1] + WINDOW_PADDING_Y

        return self.width, self.height

    def render(self, time_str: str, has_focus: bool) -> None:
        """Render the timer display."""
        # Clear canvas
        self.canvas.delete('all')

        # Draw border when focused
        if has_focus:
            self._draw_border()

        # Create and display time image
        time_image = self._create_time_image(time_str)
        self.canvas.create_image(0, 0, anchor='nw', image=time_image)

        # Prevent garbage collection
        self._time_image = time_image

    def _create_time_image(self, time_str: str) -> ImageTk.PhotoImage:
        """Create the timer display image."""
        if not self.font:
            raise ValueError("Font must be loaded before creating image")

        # Create a transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate text dimensions to center it
        bbox = draw.textbbox((0, 0), time_str, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1] - TEXT_HEIGHT_ADJUSTMENT

        # Calculate position to center text vertically
        x_pos = TEXT_OFFSET_X
        y_pos = (self.height - text_height) // 2 + TEXT_OFFSET_Y

        # Draw text in green
        draw.text((x_pos, y_pos), time_str, fill=COLOR_TIMER_TEXT, font=self.font)

        return ImageTk.PhotoImage(img)

    def _draw_border(self) -> None:
        """Draw a border around the display when focused."""
        self.canvas.create_rectangle(
            1, 1, self.width - 1, self.height - 1,
            outline=COLOR_BORDER_FOCUSED,
            width=1
        )