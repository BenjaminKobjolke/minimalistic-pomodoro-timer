"""Main application coordinator for the Pomodoro Timer."""

import tkinter as tk
from core.constants import (
    COLOR_BACKGROUND, DISPLAY_UPDATE_INTERVAL_MS
)
from core.timer_logic import TimerCore
from config.settings_manager import SettingsManager
from ui.window_manager import WindowManager
from ui.display_renderer import DisplayRenderer
from ui.tooltip import TooltipManager
from ui.input_handler import InputHandler
from logger import Logger


class PomodoroApp:
    """Main application class that coordinates all components."""

    def __init__(self):
        self.logger = Logger()
        self.logger.info("Initializing Pomodoro Timer Application")

        # Create main window
        self.window = tk.Tk()

        # Initialize components
        self.settings = SettingsManager()
        self.timer = TimerCore(self.settings.get_custom_duration_minutes() * 60)
        self.window_manager = WindowManager(self.window)
        self.tooltip_manager = TooltipManager(self.window)
        self.input_handler = InputHandler(self.window)

        # Setup UI components
        self._setup_canvas()
        self.display_renderer = DisplayRenderer(self.window, self.canvas)

        # Load settings and configure
        self._load_and_apply_settings()

        # Wire up components
        self._setup_callbacks()

        # Setup input bindings
        self.input_handler.setup_bindings()

        # Initial display update
        self.window.update()
        self.update_display()

    def _setup_canvas(self) -> None:
        """Create and setup the main canvas."""
        # Create a temporary canvas to get dimensions
        temp_canvas = tk.Canvas(self.window)

        # We'll set the actual size after loading the font
        self.canvas = temp_canvas

    def _load_and_apply_settings(self) -> None:
        """Load settings and apply them to components."""
        # Apply window position
        x, y = self.settings.get_window_position()
        self.window_manager.set_position(x, y)

        # Load font
        font_size = self.settings.get_font_size()
        font_path = self.settings.get_font_path()
        self.display_renderer.load_font(font_path, font_size)

        # Calculate dimensions and resize canvas
        width, height = self.display_renderer.calculate_dimensions()
        self.canvas.config(
            width=width,
            height=height,
            bg=COLOR_BACKGROUND,
            highlightthickness=0
        )
        self.canvas.pack()

    def _setup_callbacks(self) -> None:
        """Wire up callbacks between components."""
        # Input handler callbacks
        self.input_handler.set_timer_toggle_callback(self.toggle_timer)
        self.input_handler.set_timer_reset_callback(self.reset_timer)
        self.input_handler.set_duration_prompt_callback(self.prompt_duration)
        self.input_handler.set_always_on_top_callback(self.toggle_always_on_top)
        self.input_handler.set_move_callback(self.window_manager.move_window)
        self.input_handler.set_destroy_callback(self.save_settings)

        # Window manager focus callback
        self.window_manager.set_focus_callback(self.update_display)

    def toggle_timer(self) -> None:
        """Toggle the timer between running and paused states."""
        self.timer.toggle()
        self.update_display()

    def reset_timer(self) -> None:
        """Reset the timer to default duration."""
        self.timer.reset()
        self.update_display()

    def prompt_duration(self) -> None:
        """Prompt for and set a new timer duration."""
        new_duration = self.input_handler.prompt_for_duration()
        if new_duration is not None:
            self.timer.set_duration(new_duration)
            self.settings.set_custom_duration_minutes(new_duration)
            self.settings.save_settings()
            self.reset_timer()
            self.logger.info(f"Timer duration set to {new_duration} minutes")

    def toggle_always_on_top(self) -> None:
        """Toggle the always-on-top window state."""
        is_on_top = self.window_manager.toggle_always_on_top()
        status = "ON" if is_on_top else "OFF"
        self.tooltip_manager.show(f"Always on top: {status}")

    def update_display(self) -> None:
        """Update the timer display."""
        # Update timer state
        self.timer.update()

        # Get formatted time
        time_str = self.timer.get_formatted_time()

        # Render display
        has_focus = self.window_manager.has_focus()
        self.display_renderer.render(time_str, has_focus)

        # Schedule next update if running
        if self.timer.is_running():
            self.window.after(DISPLAY_UPDATE_INTERVAL_MS, self.update_display)

    def save_settings(self) -> None:
        """Save current settings."""
        x, y = self.window_manager.get_position()
        self.settings.set_window_position(x, y)
        self.settings.save_settings()

    def run(self) -> None:
        """Start the application main loop."""
        self.logger.info("Starting application main loop")
        self.window.mainloop()