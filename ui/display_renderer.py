"""Display rendering for the Pomodoro Timer application."""

import tkinter as tk
from typing import Optional
from PIL import Image, ImageFont, ImageDraw, ImageTk
from core.constants import (
    COLOR_TIMER_TEXT, COLOR_BACKGROUND, COLOR_BORDER_FOCUSED,
    COLOR_WORK_TIMER_DEFAULT, COLOR_PAUSE_TIMER_DEFAULT,
    WINDOW_PADDING_X, WINDOW_PADDING_Y,
    TEXT_OFFSET_X, TEXT_OFFSET_Y, TEXT_HEIGHT_ADJUSTMENT,
    DEFAULT_FONT_FILE, DEFAULT_FONT_SIZE,
    TIMER_PHASE_WORK, TIMER_PHASE_PAUSE
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

        # Color settings for different timer phases
        self.work_timer_color = COLOR_WORK_TIMER_DEFAULT
        self.pause_timer_color = COLOR_PAUSE_TIMER_DEFAULT

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

    def render(self, time_str: str, has_focus: bool, timer_phase: str = TIMER_PHASE_WORK) -> None:
        """Render the timer display."""
        # Clear canvas
        self.canvas.delete('all')

        # Draw border when focused
        if has_focus:
            self._draw_border()

        # Create and display time image
        time_image = self._create_time_image(time_str, timer_phase)
        self.canvas.create_image(0, 0, anchor='nw', image=time_image)

        # Prevent garbage collection
        self._time_image = time_image

    def _create_time_image(self, time_str: str, timer_phase: str = TIMER_PHASE_WORK) -> ImageTk.PhotoImage:
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

        # Choose color based on timer phase
        text_color = self._get_phase_color(timer_phase)

        # Draw text with phase-appropriate color
        draw.text((x_pos, y_pos), time_str, fill=text_color, font=self.font)

        return ImageTk.PhotoImage(img)

    def _get_phase_color(self, timer_phase: str) -> str:
        """Get the appropriate color for the given timer phase."""
        if timer_phase == TIMER_PHASE_PAUSE:
            return self.pause_timer_color
        else:  # TIMER_PHASE_WORK or default
            return self.work_timer_color

    def set_work_timer_color(self, color: str) -> None:
        """Set the work timer color."""
        self.work_timer_color = color
        self.logger.info(f"Work timer color updated to: {color}")

    def set_pause_timer_color(self, color: str) -> None:
        """Set the pause timer color."""
        self.pause_timer_color = color
        self.logger.info(f"Pause timer color updated to: {color}")

    def update_colors(self, work_color: str, pause_color: str) -> None:
        """Update both timer colors at once."""
        self.work_timer_color = work_color
        self.pause_timer_color = pause_color
        self.logger.info(f"Timer colors updated - Work: {work_color}, Pause: {pause_color}")

    def _draw_border(self) -> None:
        """Draw a border around the display when focused."""
        self.canvas.create_rectangle(
            1, 1, self.width - 1, self.height - 1,
            outline=COLOR_BORDER_FOCUSED,
            width=1
        )