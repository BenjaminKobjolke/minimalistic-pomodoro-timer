"""Configuration window for the Pomodoro Timer application."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from config.settings_manager import SettingsManager
from ui.color_picker import ColorPickerFrame
from core.constants import CONFIG_WINDOW_WIDTH, CONFIG_WINDOW_HEIGHT
from logger import Logger


class ConfigWindow:
    """Configuration window for managing timer settings."""

    def __init__(self, parent_window: tk.Tk, settings_manager: SettingsManager):
        self.parent_window = parent_window
        self.settings = settings_manager
        self.logger = Logger()
        self.window: Optional[tk.Toplevel] = None
        self.on_settings_changed: Optional[Callable] = None

        # Widget variables
        self.work_duration_var = tk.StringVar()
        self.pause_duration_var = tk.StringVar()
        self.always_on_top_var = tk.BooleanVar()
        self.show_work_alert_var = tk.BooleanVar()
        self.show_pause_alert_var = tk.BooleanVar()

        # Color picker widgets
        self.work_color_picker: Optional[ColorPickerFrame] = None
        self.pause_color_picker: Optional[ColorPickerFrame] = None

    def show(self) -> None:
        """Show the configuration window."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_set()
            return

        self._create_window()
        self._load_current_settings()

    def _create_window(self) -> None:
        """Create the configuration window."""
        self.window = tk.Toplevel(self.parent_window)
        self.window.title("Pomodoro Timer Configuration")
        self.window.geometry(f"{CONFIG_WINDOW_WIDTH}x{CONFIG_WINDOW_HEIGHT}")
        self.window.resizable(False, False)
        self.window.transient(self.parent_window)
        self.window.grab_set()

        # Center the window
        self._center_window()

        # Create the main notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self._create_timer_tab(notebook)
        self._create_display_tab(notebook)
        self._create_alerts_tab(notebook)

        # Create buttons frame
        self._create_buttons_frame()

    def _center_window(self) -> None:
        """Center the configuration window on screen."""
        if not self.window:
            return

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width // 2) - (CONFIG_WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (CONFIG_WINDOW_HEIGHT // 2)

        self.window.geometry(f"{CONFIG_WINDOW_WIDTH}x{CONFIG_WINDOW_HEIGHT}+{x}+{y}")

    def _create_timer_tab(self, notebook: ttk.Notebook) -> None:
        """Create the timer settings tab."""
        timer_frame = ttk.Frame(notebook)
        notebook.add(timer_frame, text="Timer")

        # Work duration
        ttk.Label(timer_frame, text="Work Duration (minutes):").grid(
            row=0, column=0, padx=10, pady=10, sticky='w'
        )
        work_duration_entry = ttk.Entry(
            timer_frame, textvariable=self.work_duration_var, width=10
        )
        work_duration_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # Pause duration
        ttk.Label(timer_frame, text="Pause Duration (minutes):").grid(
            row=1, column=0, padx=10, pady=10, sticky='w'
        )
        pause_duration_entry = ttk.Entry(
            timer_frame, textvariable=self.pause_duration_var, width=10
        )
        pause_duration_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(
            timer_frame,
            text="(Set to 0 to disable pause phase)",
            font=('TkDefaultFont', 8)
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='w')

        # Always on top checkbox
        always_on_top_check = ttk.Checkbutton(
            timer_frame,
            text="Always on top",
            variable=self.always_on_top_var
        )
        always_on_top_check.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='w')

    def _create_display_tab(self, notebook: ttk.Notebook) -> None:
        """Create the display settings tab."""
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="Display")

        # Work timer color
        ttk.Label(display_frame, text="Work Timer Color:").grid(
            row=0, column=0, padx=10, pady=10, sticky='w'
        )
        self.work_color_picker = ColorPickerFrame(
            display_frame, "", self.settings.get_work_timer_color()
        )
        self.work_color_picker.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # Pause timer color
        ttk.Label(display_frame, text="Pause Timer Color:").grid(
            row=1, column=0, padx=10, pady=10, sticky='w'
        )
        self.pause_color_picker = ColorPickerFrame(
            display_frame, "", self.settings.get_pause_timer_color()
        )
        self.pause_color_picker.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    def _create_alerts_tab(self, notebook: ttk.Notebook) -> None:
        """Create the alerts settings tab."""
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Alerts")

        # Work completion alert
        work_alert_check = ttk.Checkbutton(
            alerts_frame,
            text="Show alert when pomodoro is over",
            variable=self.show_work_alert_var
        )
        work_alert_check.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Pause completion alert
        pause_alert_check = ttk.Checkbutton(
            alerts_frame,
            text="Show alert when pause is over",
            variable=self.show_pause_alert_var
        )
        pause_alert_check.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    def _create_buttons_frame(self) -> None:
        """Create the buttons at the bottom of the window."""
        if not self.window:
            return

        buttons_frame = ttk.Frame(self.window)
        buttons_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        # Buttons
        ttk.Button(
            buttons_frame,
            text="Apply",
            command=self._apply_settings
        ).pack(side='left', padx=(0, 5))

        ttk.Button(
            buttons_frame,
            text="OK",
            command=self._ok_button_clicked
        ).pack(side='left', padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel_button_clicked
        ).pack(side='left', padx=5)

    def _load_current_settings(self) -> None:
        """Load current settings into the form."""
        # Timer settings
        self.work_duration_var.set(str(self.settings.get_custom_duration_minutes()))
        self.pause_duration_var.set(str(self.settings.get_pause_duration_minutes()))
        self.always_on_top_var.set(self.settings.get_always_on_top())

        # Alert settings
        self.show_work_alert_var.set(self.settings.get_show_work_alert())
        self.show_pause_alert_var.set(self.settings.get_show_pause_alert())

        # Colors are already loaded in the color pickers

    def _apply_settings(self) -> None:
        """Apply the current settings."""
        try:
            # Validate and apply timer durations
            work_duration = int(self.work_duration_var.get())
            pause_duration = int(self.pause_duration_var.get())

            if work_duration <= 0:
                raise ValueError("Work duration must be greater than 0")
            if pause_duration < 0:
                raise ValueError("Pause duration cannot be negative")

            # Save timer settings
            self.settings.set_custom_duration_minutes(work_duration)
            self.settings.set_pause_duration_minutes(pause_duration)
            self.settings.set_always_on_top(self.always_on_top_var.get())

            # Save display settings
            if self.work_color_picker:
                self.settings.set_work_timer_color(self.work_color_picker.get_color())
            if self.pause_color_picker:
                self.settings.set_pause_timer_color(self.pause_color_picker.get_color())

            # Save alert settings
            self.settings.set_show_work_alert(self.show_work_alert_var.get())
            self.settings.set_show_pause_alert(self.show_pause_alert_var.get())

            # Save to file
            self.settings.save_settings()

            # Notify that settings changed
            if self.on_settings_changed:
                self.on_settings_changed()

            self.logger.info("Settings applied successfully")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input:\n{e}")
        except Exception as e:
            self.logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Error", f"Failed to apply settings:\n{e}")

    def _ok_button_clicked(self) -> None:
        """Handle OK button click."""
        self._apply_settings()
        self._close_window()

    def _cancel_button_clicked(self) -> None:
        """Handle Cancel button click."""
        self._close_window()

    def _close_window(self) -> None:
        """Close the configuration window."""
        if self.window:
            self.window.destroy()
            self.window = None

    def set_settings_changed_callback(self, callback: Callable) -> None:
        """Set callback for when settings are applied."""
        self.on_settings_changed = callback