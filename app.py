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
from ui.alert_manager import AlertManager
from ui.config_window import ConfigWindow
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
        self.timer = TimerCore(
            work_duration_seconds=self.settings.get_custom_duration_minutes() * 60,
            pause_duration_seconds=self.settings.get_pause_duration_minutes() * 60
        )
        self.window_manager = WindowManager(self.window)
        self.tooltip_manager = TooltipManager(self.window)
        self.input_handler = InputHandler(self.window)
        self.alert_manager = AlertManager(self.window)
        self.config_window = ConfigWindow(self.window, self.settings)

        # Setup UI components
        self._setup_canvas()
        self.display_renderer = DisplayRenderer(self.window, self.canvas)

        # Load settings and configure
        self._load_and_apply_settings()

        # Wire up components
        self._setup_callbacks()

        # Setup input bindings
        self.input_handler.setup_bindings()

        # Apply always-on-top setting from config
        self.window_manager.always_on_top = self.settings.get_always_on_top()
        self.window.attributes('-topmost', self.window_manager.always_on_top)

        # Initial display update
        self.window.update()
        self.update_display()

        # Apply window position AFTER window is fully constructed and realized
        self._apply_saved_window_position()

    def _setup_canvas(self) -> None:
        """Create and setup the main canvas."""
        # Create a temporary canvas to get dimensions
        temp_canvas = tk.Canvas(self.window)

        # We'll set the actual size after loading the font
        self.canvas = temp_canvas

    def _load_and_apply_settings(self) -> None:
        """Load settings and apply them to components."""
        # Load font and colors (but delay window position until after window is fully realized)
        font_size = self.settings.get_font_size()
        font_path = self.settings.get_font_path()
        self.display_renderer.load_font(font_path, font_size)

        # Load timer colors
        work_color = self.settings.get_work_timer_color()
        pause_color = self.settings.get_pause_timer_color()
        self.display_renderer.update_colors(work_color, pause_color)

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
        self.input_handler.set_config_window_callback(self.show_config_window)

        # Window manager focus callback
        self.window_manager.set_focus_callback(self.update_display)

        # Timer phase completion callbacks
        self.timer.set_work_complete_callback(self._on_work_complete)
        self.timer.set_pause_complete_callback(self._on_pause_complete)

        # Config window callback
        self.config_window.set_settings_changed_callback(self._on_settings_changed)

    def toggle_timer(self) -> None:
        """Toggle the timer between running and paused states."""
        self.timer.toggle()
        self.update_display()

    def reset_timer(self) -> None:
        """Reset the timer to default duration."""
        self.timer.reset()
        self.update_display()

    def prompt_duration(self) -> None:
        """Prompt for and set a new work timer duration (legacy method)."""
        new_duration = self.input_handler.prompt_for_duration()
        if new_duration is not None:
            self.timer.set_work_duration(new_duration)
            self.settings.set_custom_duration_minutes(new_duration)
            self.settings.save_settings()
            self.reset_timer()
            self.logger.info(f"Work timer duration set to {new_duration} minutes")

    def toggle_always_on_top(self) -> None:
        """Toggle the always-on-top window state."""
        is_on_top = self.window_manager.toggle_always_on_top()
        status = "ON" if is_on_top else "OFF"
        self.tooltip_manager.show(f"Always on top: {status}")

    def update_display(self) -> None:
        """Update the timer display."""
        # Update timer state
        self.timer.update()

        # Get formatted time and current phase
        time_str = self.timer.get_formatted_time()
        current_phase = self.timer.get_current_phase()

        # Render display with phase-appropriate color
        has_focus = self.window_manager.has_focus()
        self.display_renderer.render(time_str, has_focus, current_phase)

        # Schedule next update if running
        if self.timer.is_running():
            self.window.after(DISPLAY_UPDATE_INTERVAL_MS, self.update_display)

    def show_config_window(self) -> None:
        """Show the configuration window."""
        self.config_window.show()

    def _on_work_complete(self) -> None:
        """Handle work phase completion."""
        if self.settings.get_show_work_alert():
            self.alert_manager.show_work_complete_alert()

    def _on_pause_complete(self) -> None:
        """Handle pause phase completion."""
        if self.settings.get_show_pause_alert():
            self.alert_manager.show_pause_complete_alert()

    def _on_settings_changed(self) -> None:
        """Handle settings changes from config window."""
        # Reload timer durations
        work_duration = self.settings.get_custom_duration_minutes() * 60
        pause_duration = self.settings.get_pause_duration_minutes() * 60
        self.timer.set_work_duration(work_duration // 60)
        self.timer.set_pause_duration(pause_duration // 60)

        # Reload colors
        work_color = self.settings.get_work_timer_color()
        pause_color = self.settings.get_pause_timer_color()
        self.display_renderer.update_colors(work_color, pause_color)

        # Update always-on-top setting
        always_on_top = self.settings.get_always_on_top()
        if always_on_top != self.window_manager.always_on_top:
            self.window_manager.always_on_top = always_on_top
            self.window.attributes('-topmost', always_on_top)

        # Reset timer to apply new durations
        self.reset_timer()

        self.logger.info("Settings reloaded from configuration")

    def _apply_saved_window_position(self) -> None:
        """Apply the saved window position after the window is fully realized."""
        # Get saved position
        x, y = self.settings.get_window_position()

        # Ensure window is fully processed before setting position
        self.window.update_idletasks()

        # Set the position
        self.window_manager.set_position(x, y)

        # Force another update to make sure position takes effect
        self.window.update()

        self.logger.info(f"Applied saved window position: ({x}, {y})")

    def save_settings(self) -> None:
        """Save current settings."""
        x, y = self.window_manager.get_position()
        self.settings.set_window_position(x, y)
        self.settings.save_settings()

    def run(self) -> None:
        """Start the application main loop."""
        self.logger.info("Starting application main loop")
        self.window.mainloop()