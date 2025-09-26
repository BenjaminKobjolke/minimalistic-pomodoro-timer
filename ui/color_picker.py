"""Color picker widget for the configuration window."""

import tkinter as tk
from tkinter import colorchooser, ttk
from typing import Callable, Optional
from logger import Logger


class ColorPickerFrame:
    """A color picker frame widget with preview and button."""

    def __init__(self, parent: tk.Widget, label_text: str, initial_color: str = '#000000'):
        self.parent = parent
        self.logger = Logger()
        self.current_color = initial_color
        self.on_color_changed: Optional[Callable[[str], None]] = None

        self.frame = ttk.Frame(parent)
        self._create_widgets(label_text)

    def _create_widgets(self, label_text: str) -> None:
        """Create the color picker widgets."""
        # Label
        self.label = ttk.Label(self.frame, text=label_text)
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Color preview canvas
        self.color_canvas = tk.Canvas(
            self.frame,
            width=40,
            height=20,
            relief='sunken',
            borderwidth=1
        )
        self.color_canvas.grid(row=0, column=1, padx=5, pady=5)
        self._update_color_preview()

        # Color picker button
        self.pick_button = ttk.Button(
            self.frame,
            text="Choose Color",
            command=self._open_color_dialog
        )
        self.pick_button.grid(row=0, column=2, padx=5, pady=5)

        # Color hex entry
        self.color_var = tk.StringVar(value=self.current_color)
        self.color_entry = ttk.Entry(
            self.frame,
            textvariable=self.color_var,
            width=10
        )
        self.color_entry.grid(row=0, column=3, padx=5, pady=5)
        self.color_entry.bind('<Return>', self._on_manual_color_entry)
        self.color_entry.bind('<FocusOut>', self._on_manual_color_entry)

    def _update_color_preview(self) -> None:
        """Update the color preview canvas."""
        try:
            self.color_canvas.delete('all')
            self.color_canvas.create_rectangle(
                0, 0, 40, 20,
                fill=self.current_color,
                outline='gray'
            )
        except tk.TclError:
            # Invalid color format, show white
            self.color_canvas.delete('all')
            self.color_canvas.create_rectangle(
                0, 0, 40, 20,
                fill='white',
                outline='gray'
            )

    def _open_color_dialog(self) -> None:
        """Open the color chooser dialog."""
        try:
            color = colorchooser.askcolor(
                color=self.current_color,
                parent=self.parent,
                title=f"Choose {self.label.cget('text')}"
            )

            if color[1]:  # User selected a color (not cancelled)
                self.set_color(color[1])
        except Exception as e:
            self.logger.error(f"Error opening color dialog: {e}")

    def _on_manual_color_entry(self, event: Optional[tk.Event] = None) -> None:
        """Handle manual color entry."""
        new_color = self.color_var.get().strip()
        if new_color != self.current_color:
            self.set_color(new_color)

    def set_color(self, color: str) -> None:
        """Set the current color."""
        if self._is_valid_color(color):
            self.current_color = color
            self.color_var.set(color)
            self._update_color_preview()

            if self.on_color_changed:
                self.on_color_changed(color)

            self.logger.info(f"Color changed to: {color}")
        else:
            # Revert to previous color
            self.color_var.set(self.current_color)
            self.logger.warning(f"Invalid color format: {color}")

    def _is_valid_color(self, color: str) -> bool:
        """Check if the color string is valid."""
        try:
            # Try to use the color in a temporary canvas to validate
            temp_canvas = tk.Canvas(self.frame, width=1, height=1)
            temp_canvas.create_rectangle(0, 0, 1, 1, fill=color)
            temp_canvas.destroy()
            return True
        except tk.TclError:
            return False

    def get_color(self) -> str:
        """Get the current color."""
        return self.current_color

    def set_color_changed_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback for when color changes."""
        self.on_color_changed = callback

    def pack(self, **kwargs) -> None:
        """Pack the color picker frame."""
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        """Grid the color picker frame."""
        self.frame.grid(**kwargs)