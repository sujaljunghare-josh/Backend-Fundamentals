import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Generate log filename with timestamp
LOG_FILE = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"

# Custom formatter for colored console output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: blue + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

def setup_logger(name: str = "event_rsvp_api") -> logging.Logger:
    """
    Set up logger with both console and file handlers.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler (colored output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    
    # File handler (detailed logs)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Create default logger
logger = setup_logger()