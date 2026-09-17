"""Logging to the console and to reports/test_execution.log."""

import logging
import sys

from utils.config import Config

_ready = False


def configure_logging():
    global _ready
    if _ready:
        return

    Config.ensure_directories()
    logger = logging.getLogger("orangehrm")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(Config.LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _ready = True


def get_logger(name):
    configure_logging()
    return logging.getLogger(f"orangehrm.{name}")
