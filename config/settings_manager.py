"""Settings management for the Pomodoro Timer application."""

import configparser
from typing import Tuple, Optional
from core.constants import (
    DEFAULT_WINDOW_X, DEFAULT_WINDOW_Y,
    DEFAULT_FONT_SIZE, DEFAULT_DURATION_MINUTES, DEFAULT_PAUSE_DURATION_MINUTES,
    COLOR_WORK_TIMER_DEFAULT, COLOR_PAUSE_TIMER_DEFAULT,
    DEFAULT_SHOW_WORK_ALERT, DEFAULT_SHOW_PAUSE_ALERT
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

    def get_pause_duration_minutes(self) -> int:
        """Get the pause timer duration in minutes."""
        try:
            if self.config.has_section('Timer') and self.config.has_option('Timer', 'pause_duration_minutes'):
                duration = self.config.getint('Timer', 'pause_duration_minutes')
                if duration >= 0:  # 0 means no pause phase
                    return duration
                else:
                    self.logger.warning("Invalid pause_duration_minutes in settings, using default")
        except (ValueError, configparser.Error) as e:
            self.logger.warning(f"Error reading pause duration: {e}")

        return DEFAULT_PAUSE_DURATION_MINUTES

    def set_pause_duration_minutes(self, minutes: int) -> None:
        """Set the pause timer duration in minutes."""
        if not self.config.has_section('Timer'):
            self.config.add_section('Timer')

        self.config.set('Timer', 'pause_duration_minutes', str(minutes))
        self.logger.info(f"Pause duration set to: {minutes} minutes")

    def get_work_timer_color(self) -> str:
        """Get the work timer text color."""
        if self.config.has_section('Display') and self.config.has_option('Display', 'work_timer_color'):
            return self.config.get('Display', 'work_timer_color')
        return COLOR_WORK_TIMER_DEFAULT

    def set_work_timer_color(self, color: str) -> None:
        """Set the work timer text color."""
        if not self.config.has_section('Display'):
            self.config.add_section('Display')

        self.config.set('Display', 'work_timer_color', color)
        self.logger.info(f"Work timer color set to: {color}")

    def get_pause_timer_color(self) -> str:
        """Get the pause timer text color."""
        if self.config.has_section('Display') and self.config.has_option('Display', 'pause_timer_color'):
            return self.config.get('Display', 'pause_timer_color')
        return COLOR_PAUSE_TIMER_DEFAULT

    def set_pause_timer_color(self, color: str) -> None:
        """Set the pause timer text color."""
        if not self.config.has_section('Display'):
            self.config.add_section('Display')

        self.config.set('Display', 'pause_timer_color', color)
        self.logger.info(f"Pause timer color set to: {color}")

    def get_show_work_alert(self) -> bool:
        """Get whether to show work completion alert."""
        if self.config.has_section('Alerts') and self.config.has_option('Alerts', 'show_work_complete_alert'):
            return self.config.getboolean('Alerts', 'show_work_complete_alert')
        return DEFAULT_SHOW_WORK_ALERT

    def set_show_work_alert(self, show: bool) -> None:
        """Set whether to show work completion alert."""
        if not self.config.has_section('Alerts'):
            self.config.add_section('Alerts')

        self.config.set('Alerts', 'show_work_complete_alert', str(show))
        self.logger.info(f"Show work complete alert set to: {show}")

    def get_show_pause_alert(self) -> bool:
        """Get whether to show pause completion alert."""
        if self.config.has_section('Alerts') and self.config.has_option('Alerts', 'show_pause_complete_alert'):
            return self.config.getboolean('Alerts', 'show_pause_complete_alert')
        return DEFAULT_SHOW_PAUSE_ALERT

    def set_show_pause_alert(self, show: bool) -> None:
        """Set whether to show pause completion alert."""
        if not self.config.has_section('Alerts'):
            self.config.add_section('Alerts')

        self.config.set('Alerts', 'show_pause_complete_alert', str(show))
        self.logger.info(f"Show pause complete alert set to: {show}")

    def get_always_on_top(self) -> bool:
        """Get the always-on-top setting."""
        if self.config.has_section('Window') and self.config.has_option('Window', 'always_on_top'):
            return self.config.getboolean('Window', 'always_on_top')
        return True  # Default to True as it was the original behavior

    def set_always_on_top(self, always_on_top: bool) -> None:
        """Set the always-on-top setting."""
        if not self.config.has_section('Window'):
            self.config.add_section('Window')

        self.config.set('Window', 'always_on_top', str(always_on_top))
        self.logger.info(f"Always on top set to: {always_on_top}")

    def _create_default_config(self) -> None:
        """Create a default configuration."""
        self.config['Window'] = {
            'x': str(DEFAULT_WINDOW_X),
            'y': str(DEFAULT_WINDOW_Y),
            'always_on_top': str(True)
        }
        self.config['Display'] = {
            'font_size': str(DEFAULT_FONT_SIZE),
            'work_timer_color': COLOR_WORK_TIMER_DEFAULT,
            'pause_timer_color': COLOR_PAUSE_TIMER_DEFAULT
        }
        self.config['Timer'] = {
            'custom_duration_minutes': str(DEFAULT_DURATION_MINUTES),
            'pause_duration_minutes': str(DEFAULT_PAUSE_DURATION_MINUTES)
        }
        self.config['Alerts'] = {
            'show_work_complete_alert': str(DEFAULT_SHOW_WORK_ALERT),
            'show_pause_complete_alert': str(DEFAULT_SHOW_PAUSE_ALERT)
        }
        self.logger.info("Default configuration created")