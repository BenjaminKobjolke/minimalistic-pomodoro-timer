"""Alert management for timer completion notifications."""

import tkinter as tk
from tkinter import messagebox
from logger import Logger


class AlertManager:
    """Manages alert notifications for timer completion events."""

    def __init__(self, parent_window: tk.Tk):
        self.parent_window = parent_window
        self.logger = Logger()

    def show_work_complete_alert(self) -> None:
        """Show alert when work timer (pomodoro) completes."""
        try:
            messagebox.showinfo(
                "Pomodoro Complete!",
                "Work session finished!\n\nTime for a break.",
                parent=self.parent_window
            )
            self.logger.info("Work completion alert shown")
        except Exception as e:
            self.logger.error(f"Error showing work completion alert: {e}")

    def show_pause_complete_alert(self) -> None:
        """Show alert when pause timer (break) completes."""
        try:
            messagebox.showinfo(
                "Break Complete!",
                "Break time is over!\n\nReady to get back to work?",
                parent=self.parent_window
            )
            self.logger.info("Pause completion alert shown")
        except Exception as e:
            self.logger.error(f"Error showing pause completion alert: {e}")

    def show_custom_alert(self, title: str, message: str) -> None:
        """Show a custom alert dialog."""
        try:
            messagebox.showinfo(title, message, parent=self.parent_window)
            self.logger.info(f"Custom alert shown: {title}")
        except Exception as e:
            self.logger.error(f"Error showing custom alert: {e}")