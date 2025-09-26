#!/usr/bin/env python3
"""
Minimalistic Pomodoro Timer
A simple, transparent Pomodoro timer with keyboard controls.

Controls:
- 's' to start/pause timer
- 'r' to reset timer
- 'e' to set custom duration (legacy)
- 'c' to open configuration window
- 'a' to toggle always-on-top mode
- Arrow keys to move window
- Shift + Arrow keys for fine movement
"""

from app import PomodoroApp
from logger import Logger

def main() -> None:
    """Main entry point for the Pomodoro Timer application."""
    logger = Logger()
    logger.info("Starting Pomodoro Timer application")

    try:
        app = PomodoroApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
