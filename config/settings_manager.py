"""Settings management for the Pomodoro Timer application."""

import configparser
from typing import Tuple, Optional
from core.constants import (
    DEFAULT_WINDOW_X, DEFAULT_WINDOW_Y,
    DEFAULT_FONT_SIZE, DEFAULT_DURATION_MINUTES
)
from logger import Logger


class SettingsManager:
    """Manages loading and saving application settings."""

    def __init__(self):
        self.logger = Logger()
        self.config = configparser.ConfigParser()
        self.config_file = 'settings.ini'
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from the configuration file."""
        try:
            self.config.read(self.config_file)
            self.logger.info("Settings loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            self._create_default_config()

    def save_settings(self) -> None:
        """Save current settings to the configuration file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def get_window_position(self) -> Tuple[int, int]:
        """Get the saved window position."""
        try:
            if self.config.has_section('Window'):
                x = self.config.getint('Window', 'x')
                y = self.config.getint('Window', 'y')
                return x, y
        except (ValueError, configparser.Error) as e:
            self.logger.warning(f"Invalid window position in settings: {e}")

        return DEFAULT_WINDOW_X, DEFAULT_WINDOW_Y

    def set_window_position(self, x: int, y: int) -> None:
        """Save the window position."""
        if not self.config.has_section('Window'):
            self.config.add_section('Window')

        self.config.set('Window', 'x', str(x))
        self.config.set('Window', 'y', str(y))

    def get_font_size(self) -> int:
        """Get the saved font size."""
        try:
            if self.config.has_section('Display'):
                return self.config.getint('Display', 'font_size')
        except (ValueError, configparser.Error) as e:
            self.logger.warning(f"Invalid font size in settings: {e}")

        return DEFAULT_FONT_SIZE

    def get_font_path(self) -> Optional[str]:
        """Get the custom font path if specified."""
        if self.config.has_section('Display') and self.config.has_option('Display', 'font_path'):
            return self.config.get('Display', 'font_path')
        return None

    def get_custom_duration_minutes(self) -> int:
        """Get the custom timer duration in minutes."""
        try:
            if self.config.has_section('Timer') and self.config.has_option('Timer', 'custom_duration_minutes'):
                duration = self.config.getint('Timer', 'custom_duration_minutes')
                if duration > 0:
                    self.logger.info(f"Loaded custom duration: {duration} minutes")
                    return duration
                else:
                    self.logger.warning("Invalid custom_duration_minutes in settings, using default")
        except (ValueError, configparser.Error) as e:
            self.logger.warning(f"Error reading custom duration: {e}")

        self.logger.info("Using default timer duration")
        return DEFAULT_DURATION_MINUTES

    def set_custom_duration_minutes(self, minutes: int) -> None:
        """Set the custom timer duration in minutes."""
        if not self.config.has_section('Timer'):
            self.config.add_section('Timer')

        self.config.set('Timer', 'custom_duration_minutes', str(minutes))
        self.logger.info(f"Custom duration set to: {minutes} minutes")

    def _create_default_config(self) -> None:
        """Create a default configuration."""
        self.config['Window'] = {
            'x': str(DEFAULT_WINDOW_X),
            'y': str(DEFAULT_WINDOW_Y)
        }
        self.config['Display'] = {
            'font_size': str(DEFAULT_FONT_SIZE)
        }
        self.config['Timer'] = {
            'custom_duration_minutes': str(DEFAULT_DURATION_MINUTES)
        }
        self.logger.info("Default configuration created")