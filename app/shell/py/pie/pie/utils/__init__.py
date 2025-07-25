import sys

from loguru import logger

# Remove default handlers
logger.remove()

LOG_FORMAT = "{time} {module:>25}:{function:<25}:{line:<4} {level:<5} {message} {extra}"

# Configure the console sink
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="INFO",
)


def read_utf8(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_utf8(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def disable_logging():
    logger.remove()


def add_file_logger(filename, level="DEBUG"):
    logger.add(filename, format=LOG_FORMAT, level=level)
