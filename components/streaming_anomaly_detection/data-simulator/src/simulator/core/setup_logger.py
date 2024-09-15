import logging


def setup_logger(name: str, level=logging.INFO, log_format=None) -> logging.Logger:
    """
    Sets up a logger with the specified name and log level.
    Reuses the same logger if already configured.
    """
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if logger is already configured
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler()

        # Use a default log format if not provided
        if not log_format:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(handler)

    return logger
