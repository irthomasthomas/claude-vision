import logging

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, filename="claude_vision_debug.log", filemode="w")
    return logging.getLogger(__name__)

logger = setup_logging()