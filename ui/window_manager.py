"""Window management for the Pomodoro Timer application."""

import tkinter as tk
import os
from typing import Optional, Callable
from core.constants import (
    WINDOW_ALPHA, MOVE_SPEED_FAST, MOVE_SPEED_SLOW
)
from logger import Logger


class WindowManager:
    """Manages the application window properties and movement."""

    def __init__(self, window: tk.Tk):
        self.window = window
        self.logger = Logger()
        self.always_on_top = True
        self.on_focus_callback: Optional[Callable] = None

        # Track last known valid position to avoid 0,0 on window destroy
        self.last_valid_x = 0
        self.last_valid_y = 0

        # Track focus state for reliable focus detection with overrideredirect windows
        self._has_focus = False

        self._setup_window()

    def _setup_window(self) -> None:
        """Configure window properties."""
        # Set window title for Alt+Tab
        self.window.title("Pomodoro")

        # Remove all decorations
        self.window.overrideredirect(True)
        self.window.attributes('-alpha', WINDOW_ALPHA, '-topmost', self.always_on_top)

        # Keep in taskbar
        self.window.wm_attributes('-toolwindow', False)
        self.window.update_idletasks()

        # Set window style to show in Alt+Tab (Windows only)
        if os.name == 'nt':
            self._setup_windows_taskbar()

        # Bind focus events and position tracking
        self.window.bind('<FocusIn>', self._on_focus_in)
        self.window.bind('<FocusOut>', self._on_focus_out)
        self.window.bind('<Configure>', self._on_configure)

        self.logger.info("Window setup completed")

    def _setup_windows_taskbar(self) -> None:
        """Setup Windows-specific taskbar visibility."""
        try:
            import ctypes
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080

            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

            self.logger.info("Windows taskbar setup completed")
        except Exception as e:
            self.logger.warning(f"Could not setup Windows taskbar: {e}")

    def set_position(self, x: int, y: int) -> None:
        """Set the window position."""
        self.window.geometry(f'+{x}+{y}')
        # Update our tracking variables
        self.last_valid_x = x
        self.last_valid_y = y

    def get_position(self) -> tuple[int, int]:
        """Get the current window position."""
        try:
            current_x = self.window.winfo_x()
            current_y = self.window.winfo_y()

            # If we get 0,0 (likely during window destruction), return last valid position
            if current_x == 0 and current_y == 0 and (self.last_valid_x != 0 or self.last_valid_y != 0):
                self.logger.warning("Window position returned 0,0, using last valid position")
                return self.last_valid_x, self.last_valid_y

            # Update tracking if we got valid coordinates
            if current_x != 0 or current_y != 0:
                self.last_valid_x = current_x
                self.last_valid_y = current_y

            return current_x, current_y
        except tk.TclError:
            # Window might be destroyed, return last known position
            self.logger.warning("Could not get window position (window destroyed?), using last valid position")
            return self.last_valid_x, self.last_valid_y

    def move_window(self, direction: str, slow: bool = False) -> None:
        """Move window in specified direction."""
        speed = MOVE_SPEED_SLOW if slow else MOVE_SPEED_FAST
        x, y = self.get_position()

        if direction == 'left':
            x -= speed
        elif direction == 'right':
            x += speed
        elif direction == 'up':
            y -= speed
        elif direction == 'down':
            y += speed

        self.set_position(x, y)

    def _on_configure(self, event: Optional[tk.Event] = None) -> None:
        """Handle window configuration changes (including position)."""
        if event and event.widget == self.window:
            # Update our position tracking when window moves
            try:
                x = self.window.winfo_x()
                y = self.window.winfo_y()
                if x != 0 or y != 0:  # Only update if not 0,0
                    self.last_valid_x = x
                    self.last_valid_y = y
            except tk.TclError:
                pass  # Ignore if window is being destroyed

    def toggle_always_on_top(self) -> bool:
        """Toggle the always-on-top state of the window."""
        self.always_on_top = not self.always_on_top
        self.window.attributes('-topmost', self.always_on_top)
        self.logger.info(f"Always on top: {'ON' if self.always_on_top else 'OFF'}")
        return self.always_on_top

    def set_focus_callback(self, callback: Callable) -> None:
        """Set a callback to be called on focus events."""
        self.on_focus_callback = callback

    def _on_focus_in(self, event: Optional[tk.Event] = None) -> None:
        """Handle window focus in event."""
        self._has_focus = True
        if self.on_focus_callback:
            self.on_focus_callback()

    def _on_focus_out(self, event: Optional[tk.Event] = None) -> None:
        """Handle window focus out event."""
        self._has_focus = False
        if self.on_focus_callback:
            self.on_focus_callback()

    def has_focus(self) -> bool:
        """Check if the window currently has focus."""
        # Use the tracked focus state which is more reliable for borderless windows
        return self._has_focus