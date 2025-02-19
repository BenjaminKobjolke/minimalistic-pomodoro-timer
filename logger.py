import logging
from typing import Optional

ENABLE_LOGGING = False  # Set to True to enable logging to file


class Logger:
    """Custom logging class for the application."""
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self) -> None:
        """Initialize the logger with custom configuration."""
        self.logger = logging.getLogger('PomodoroTimer')
        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        if ENABLE_LOGGING:
            # Log to file
            file_handler = logging.FileHandler('pomodoro.log')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            # Use NullHandler when logging is disabled
            self.logger.addHandler(logging.NullHandler())
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)
