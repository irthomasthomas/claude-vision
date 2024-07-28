import logging
from typing import Optional
from enum import Enum
from dataclasses import dataclass

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

@dataclass
class LoggerConfig:
    name: str = __name__
    level: LogLevel = LogLevel.DEBUG
    file_name: str = "claude_vision_debug.log"
    file_mode: str = "w"
    file_level: LogLevel = LogLevel.DEBUG
    console_level: LogLevel = LogLevel.INFO
    format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class Logger:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, config: LoggerConfig = LoggerConfig()) -> logging.Logger:
        if cls._instance is None:
            cls._instance = cls._setup_logging(config)
        return cls._instance

    @staticmethod
    def _setup_logging(config: LoggerConfig) -> logging.Logger:
        logger = logging.getLogger(config.name)
        logger.setLevel(config.level.value)

        formatter = logging.Formatter(config.format_string)

        file_handler = logging.FileHandler(config.file_name, mode=config.file_mode)
        file_handler.setLevel(config.file_level.value)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.console_level.value)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

# Usage
logger = Logger.get_logger()

# Custom configuration
# custom_config = LoggerConfig(name="custom_logger", level=LogLevel.INFO, file_name="custom.log")
# custom_logger = Logger.get_logger(custom_config)