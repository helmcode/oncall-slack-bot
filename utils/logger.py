import logging
import sys

# Define log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class Logger:
    """
    Custom logger for Andulia API that outputs to standard output
    """
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_format: str = DEFAULT_LOG_FORMAT
    ):
        """
        Initialize logger with custom configuration

        Args:
            name: Logger name (usually module or component name)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Format for log messages
        """
        self.logger = logging.getLogger(name)

        # Set log level
        self.logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))

        # Create formatter
        formatter = logging.Formatter(log_format)

        # Create console handler for standard output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Remove any existing handlers to avoid duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.addHandler(console_handler)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)


# Create a function to get a preconfigured logger
def get_logger(
    name: str,
    level: str = "INFO"
) -> Logger:
    """
    Get a preconfigured logger instance that outputs to standard output

    Args:
        name: Logger name (usually module or component name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance
    """
    return Logger(name=name, level=level)
