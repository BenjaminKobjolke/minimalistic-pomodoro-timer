"""Input handling for the Pomodoro Timer application."""

import tkinter as tk
from tkinter import simpledialog
from typing import Callable, Optional, Dict
from logger import Logger


class InputHandler:
    """Manages keyboard input and bindings for the application."""

    def __init__(self, window: tk.Tk):
        self.window = window
        self.logger = Logger()
        self.callbacks: Dict[str, Callable] = {}

    def setup_bindings(self) -> None:
        """Setup all keyboard bindings."""
        # Timer controls
        self.window.bind('s', self._handle_timer_toggle)
        self.window.bind('r', self._handle_timer_reset)
        self.window.bind('e', self._handle_duration_prompt)
        self.window.bind('a', self._handle_always_on_top)
        self.window.bind('c', self._handle_config_window)

        # Movement controls
        self.window.bind('<Left>', lambda e: self._handle_move('left'))
        self.window.bind('<Right>', lambda e: self._handle_move('right'))
        self.window.bind('<Up>', lambda e: self._handle_move('up'))
        self.window.bind('<Down>', lambda e: self._handle_move('down'))

        # Fine movement controls
        self.window.bind('<Shift-Left>', lambda e: self._handle_move('left', slow=True))
        self.window.bind('<Shift-Right>', lambda e: self._handle_move('right', slow=True))
        self.window.bind('<Shift-Up>', lambda e: self._handle_move('up', slow=True))
        self.window.bind('<Shift-Down>', lambda e: self._handle_move('down', slow=True))

        # Window destroy event
        self.window.bind('<Destroy>', self._handle_destroy)

        self.logger.info("Input bindings setup completed")

    def set_timer_toggle_callback(self, callback: Callable) -> None:
        """Set callback for timer toggle action."""
        self.callbacks['timer_toggle'] = callback

    def set_timer_reset_callback(self, callback: Callable) -> None:
        """Set callback for timer reset action."""
        self.callbacks['timer_reset'] = callback

    def set_duration_prompt_callback(self, callback: Callable) -> None:
        """Set callback for duration prompt action."""
        self.callbacks['duration_prompt'] = callback

    def set_always_on_top_callback(self, callback: Callable) -> None:
        """Set callback for always-on-top toggle action."""
        self.callbacks['always_on_top'] = callback

    def set_move_callback(self, callback: Callable) -> None:
        """Set callback for window movement action."""
        self.callbacks['move'] = callback

    def set_destroy_callback(self, callback: Callable) -> None:
        """Set callback for window destroy event."""
        self.callbacks['destroy'] = callback

    def set_config_window_callback(self, callback: Callable) -> None:
        """Set callback for config window action."""
        self.callbacks['config_window'] = callback

    def prompt_for_duration(self) -> Optional[int]:
        """Show a dialog to prompt for timer duration in minutes."""
        return simpledialog.askinteger(
            "Set Timer Duration",
            "Enter duration in minutes:",
            parent=self.window,
            minvalue=1
        )

    def _handle_timer_toggle(self, event: Optional[tk.Event] = None) -> None:
        """Handle timer toggle event."""
        if 'timer_toggle' in self.callbacks:
            self.callbacks['timer_toggle']()

    def _handle_timer_reset(self, event: Optional[tk.Event] = None) -> None:
        """Handle timer reset event."""
        if 'timer_reset' in self.callbacks:
            self.callbacks['timer_reset']()

    def _handle_duration_prompt(self, event: Optional[tk.Event] = None) -> None:
        """Handle duration prompt event."""
        if 'duration_prompt' in self.callbacks:
            self.callbacks['duration_prompt']()

    def _handle_always_on_top(self, event: Optional[tk.Event] = None) -> None:
        """Handle always-on-top toggle event."""
        if 'always_on_top' in self.callbacks:
            self.callbacks['always_on_top']()

    def _handle_move(self, direction: str, slow: bool = False) -> None:
        """Handle window movement event."""
        if 'move' in self.callbacks:
            self.callbacks['move'](direction, slow)

    def _handle_destroy(self, event: Optional[tk.Event] = None) -> None:
        """Handle window destroy event."""
        if 'destroy' in self.callbacks:
            self.callbacks['destroy']()

    def _handle_config_window(self, event: Optional[tk.Event] = None) -> None:
        """Handle config window event."""
        if 'config_window' in self.callbacks:
            self.callbacks['config_window']()