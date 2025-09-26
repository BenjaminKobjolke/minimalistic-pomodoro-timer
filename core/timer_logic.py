"""Core timer logic for the Pomodoro Timer application."""

import time
from typing import Optional, Callable
from core.constants import (
    DEFAULT_DURATION_SECONDS, DEFAULT_PAUSE_DURATION_SECONDS,
    TIMER_PHASE_WORK, TIMER_PHASE_PAUSE
)
from logger import Logger


class TimerCore:
    """Handles the core timer logic without UI dependencies."""

    def __init__(self, work_duration_seconds: int = DEFAULT_DURATION_SECONDS,
                 pause_duration_seconds: int = DEFAULT_PAUSE_DURATION_SECONDS):
        self.logger = Logger()
        self.work_duration_seconds = work_duration_seconds
        self.pause_duration_seconds = pause_duration_seconds
        self.current_phase = TIMER_PHASE_WORK
        self.duration = work_duration_seconds
        self.target_end_time: Optional[float] = None
        self.running = False

        # Callbacks for phase transitions
        self.on_work_complete: Optional[Callable] = None
        self.on_pause_complete: Optional[Callable] = None

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
        """Reset timer to work phase with default duration."""
        self.current_phase = TIMER_PHASE_WORK
        self.duration = self.work_duration_seconds
        self.target_end_time = None
        self.running = False
        self.logger.info(f"Timer reset to work phase: {self.duration // 60} minutes")

    def set_work_duration(self, minutes: int) -> None:
        """Set the work timer duration in minutes."""
        if minutes > 0:
            self.work_duration_seconds = minutes * 60
            if self.current_phase == TIMER_PHASE_WORK:
                self.duration = self.work_duration_seconds
            self.logger.info(f"Work duration set to {minutes} minutes")
        else:
            self.logger.warning(f"Invalid work duration: {minutes} minutes")

    def set_pause_duration(self, minutes: int) -> None:
        """Set the pause timer duration in minutes."""
        if minutes >= 0:  # 0 means no pause phase
            self.pause_duration_seconds = minutes * 60
            if self.current_phase == TIMER_PHASE_PAUSE:
                self.duration = self.pause_duration_seconds
            self.logger.info(f"Pause duration set to {minutes} minutes")
        else:
            self.logger.warning(f"Invalid pause duration: {minutes} minutes")

    def set_duration(self, minutes: int) -> None:
        """Legacy method - sets work duration for compatibility."""
        self.set_work_duration(minutes)

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
        """Update timer state, checking if it has finished and handling phase transitions."""
        if self.is_finished():
            self.running = False
            self.target_end_time = None

            if self.current_phase == TIMER_PHASE_WORK:
                self.logger.info("Work phase finished")
                # Call work complete callback
                if self.on_work_complete:
                    self.on_work_complete()
                # Transition to pause phase if pause duration > 0
                if self.pause_duration_seconds > 0:
                    self._transition_to_pause()
            elif self.current_phase == TIMER_PHASE_PAUSE:
                self.logger.info("Pause phase finished")
                # Call pause complete callback
                if self.on_pause_complete:
                    self.on_pause_complete()
                # Transition back to work phase
                self._transition_to_work()

    def _transition_to_pause(self) -> None:
        """Transition from work phase to pause phase."""
        self.current_phase = TIMER_PHASE_PAUSE
        self.duration = self.pause_duration_seconds
        # Auto-start the pause timer
        self.start()
        self.logger.info(f"Transitioned to pause phase: {self.duration // 60} minutes (auto-started)")

    def _transition_to_work(self) -> None:
        """Transition from pause phase to work phase."""
        self.current_phase = TIMER_PHASE_WORK
        self.duration = self.work_duration_seconds
        self.logger.info(f"Transitioned to work phase: {self.duration // 60} minutes")

    def get_formatted_time(self) -> str:
        """Get the time left formatted as MM:SS."""
        time_left = self.get_time_left()
        minutes = time_left // 60
        seconds = time_left % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_current_phase(self) -> str:
        """Get the current timer phase."""
        return self.current_phase

    def is_in_work_phase(self) -> bool:
        """Check if currently in work phase."""
        return self.current_phase == TIMER_PHASE_WORK

    def is_in_pause_phase(self) -> bool:
        """Check if currently in pause phase."""
        return self.current_phase == TIMER_PHASE_PAUSE

    def set_work_complete_callback(self, callback: Callable) -> None:
        """Set callback for when work phase completes."""
        self.on_work_complete = callback

    def set_pause_complete_callback(self, callback: Callable) -> None:
        """Set callback for when pause phase completes."""
        self.on_pause_complete = callback

    def has_pause_phase(self) -> bool:
        """Check if pause phase is enabled (duration > 0)."""
        return self.pause_duration_seconds > 0