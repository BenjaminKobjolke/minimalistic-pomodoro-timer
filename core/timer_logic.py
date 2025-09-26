"""Core timer logic for the Pomodoro Timer application."""

import time
from typing import Optional
from core.constants import DEFAULT_DURATION_SECONDS
from logger import Logger


class TimerCore:
    """Handles the core timer logic without UI dependencies."""

    def __init__(self, duration_seconds: int = DEFAULT_DURATION_SECONDS):
        self.logger = Logger()
        self.default_duration_seconds = duration_seconds
        self.duration = duration_seconds
        self.target_end_time: Optional[float] = None
        self.running = False

    def start(self) -> None:
        """Start the timer."""
        if not self.running:
            self.running = True
            # Set target end time based on current time plus remaining duration
            self.target_end_time = time.time() + self.get_time_left()
            self.logger.info("Timer started")

    def pause(self) -> None:
        """Pause the timer."""
        if self.running:
            # Store remaining time when paused
            self.duration = self.get_time_left()
            self.target_end_time = None
            self.running = False
            self.logger.info("Timer paused")

    def toggle(self) -> None:
        """Toggle timer between running and paused states."""
        if self.running:
            self.pause()
        else:
            self.start()

    def reset(self) -> None:
        """Reset timer to the default duration."""
        self.duration = self.default_duration_seconds
        self.target_end_time = None
        self.running = False
        self.logger.info(f"Timer reset to {self.duration // 60} minutes")

    def set_duration(self, minutes: int) -> None:
        """Set a new timer duration in minutes."""
        if minutes > 0:
            self.default_duration_seconds = minutes * 60
            self.duration = self.default_duration_seconds
            self.logger.info(f"Timer duration set to {minutes} minutes")
        else:
            self.logger.warning(f"Invalid duration: {minutes} minutes")

    def get_time_left(self) -> int:
        """Calculate the time left based on the system clock."""
        if not self.running or self.target_end_time is None:
            return self.duration

        remaining = self.target_end_time - time.time()
        return max(0, int(remaining))

    def is_running(self) -> bool:
        """Check if the timer is currently running."""
        return self.running

    def is_finished(self) -> bool:
        """Check if the timer has finished."""
        return self.running and self.get_time_left() == 0

    def update(self) -> None:
        """Update timer state, checking if it has finished."""
        if self.is_finished():
            self.running = False
            self.target_end_time = None
            self.logger.info("Timer finished")

    def get_formatted_time(self) -> str:
        """Get the time left formatted as MM:SS."""
        time_left = self.get_time_left()
        minutes = time_left // 60
        seconds = time_left % 60
        return f"{minutes:02d}:{seconds:02d}"