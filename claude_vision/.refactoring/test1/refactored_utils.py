import logging
from typing import Optional

class LoggerSetup:
    @staticmethod
    def configure(log_level: int = logging.DEBUG,
                  log_file: str = "claude_vision_debug.log",
                  file_mode: str = "w") -> logging.Logger:
        """
        Configure and return a logger with specified settings.

        Args:
            log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO)
            log_file (str): The name of the log file
            file_mode (str): The file mode for logging ('w' for write, 'a' for append)

        Returns:
            logging.Logger: Configured logger instance
        """
        logging.basicConfig(level=log_level, 
                            filename=log_file, 
                            filemode=file_mode,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

# Create a global logger instance
logger: Optional[logging.Logger] = None

def get_logger() -> logging.Logger:
    """
    Get or create the global logger instance.

    Returns:
        logging.Logger: The configured logger instance
    """
    global logger
    if logger is None:
        logger = LoggerSetup.configure()
    return logger