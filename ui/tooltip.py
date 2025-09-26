"""Tooltip functionality for the Pomodoro Timer application."""

import tkinter as tk
from core.constants import (
    COLOR_TOOLTIP_BG, COLOR_TOOLTIP_FG,
    TOOLTIP_DURATION_MS, TOOLTIP_FONT_SIZE,
    TOOLTIP_PADDING_X, TOOLTIP_PADDING_Y,
    TOOLTIP_OFFSET_Y, TOOLTIP_HEIGHT_ESTIMATE,
    TOOLTIP_WIDTH_ESTIMATE, DEFAULT_FONT_NAME
)
from logger import Logger


class TooltipManager:
    """Manages tooltip display for the application."""

    def __init__(self, parent_window: tk.Tk):
        self.parent_window = parent_window
        self.logger = Logger()

    def show(self, message: str) -> None:
        """Display a tooltip with the given message."""
        tooltip = tk.Toplevel(self.parent_window)
        tooltip.overrideredirect(True)
        tooltip.attributes('-topmost', True)

        # Create label with message
        label = tk.Label(
            tooltip,
            text=message,
            bg=COLOR_TOOLTIP_BG,
            fg=COLOR_TOOLTIP_FG,
            font=(DEFAULT_FONT_NAME, TOOLTIP_FONT_SIZE),
            padx=TOOLTIP_PADDING_X,
            pady=TOOLTIP_PADDING_Y
        )
        label.pack()

        # Position tooltip
        self._position_tooltip(tooltip)

        # Auto-dismiss after specified duration
        tooltip.after(TOOLTIP_DURATION_MS, tooltip.destroy)

        self.logger.info(f"Tooltip shown: {message}")

    def _position_tooltip(self, tooltip: tk.Toplevel) -> None:
        """Position the tooltip relative to the parent window."""
        # Ensure tooltip dimensions are calculated
        tooltip.update_idletasks()

        # Get tooltip and parent window dimensions
        tooltip_width = tooltip.winfo_reqwidth()
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()

        # Calculate centered position below the parent window
        x = parent_x + (parent_width // 2) - (tooltip_width // 2)
        y = parent_y + parent_height + TOOLTIP_OFFSET_Y

        # Ensure tooltip stays on screen
        screen_width = self.parent_window.winfo_screenwidth()
        screen_height = self.parent_window.winfo_screenheight()

        # Adjust position if tooltip would go off screen
        if y + TOOLTIP_HEIGHT_ESTIMATE > screen_height:
            # Show above the timer if it would go below screen
            y = parent_y - TOOLTIP_HEIGHT_ESTIMATE

        if x + tooltip_width > screen_width:
            # Adjust if it would go off right edge
            x = screen_width - tooltip_width

        if x < 0:
            # Adjust if it would go off left edge
            x = 0

        tooltip.geometry(f'+{x}+{y}')