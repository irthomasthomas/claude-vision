import logging
from typing import Optional
from pathlib import Path
import os

class LoggerSetup:
    _instance: Optional[logging.Logger] = None
    LOG_FILE = Path(os.getenv("CLAUDE_VISION_LOG_FILE", "claude_vision_debug.log"))
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    FILE_LOG_LEVEL = logging.DEBUG
    CONSOLE_LOG_LEVEL = logging.INFO

    @classmethod
    def get_logger(cls, name: str = __name__) -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._setup_logging(name)
        return cls._instance

    @classmethod
    def _setup_logging(cls, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(cls.FILE_LOG_LEVEL)

        cls._add_file_handler(logger)
        cls._add_console_handler(logger)

        return logger

    @classmethod
    def _add_file_handler(cls, logger: logging.Logger) -> None:
        try:
            file_handler = logging.FileHandler(cls.LOG_FILE, mode="w")
            file_handler.setLevel(cls.FILE_LOG_LEVEL)
            file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            logger.addHandler(file_handler)
        except IOError as e:
            print(f"Warning: Unable to create log file. {e}")

    @classmethod
    def _add_console_handler(cls, logger: logging.Logger) -> None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(cls.CONSOLE_LOG_LEVEL)
        console_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        logger.addHandler(console_handler)

def get_logger(name: str = __name__) -> logging.Logger:
    return LoggerSetup.get_logger(name)

# Usage
logger = get_logger()