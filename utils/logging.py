import logging
import sys

def get_logger(name: str = "signal_detector") -> logging.Logger:
    """Return a configured logger.

    The logger logs to stdout with a simple format that includes
    timestamp, log level, and the message. It is idempotent –
    repeated calls return the same logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
