"""
Hertz Music Bot - Logging Configuration
"""

import logging
import sys
import colorlog


def setup_logging() -> None:
    """Configure structured color logging."""
    log_format = (
        "%(cyan)s%(asctime)s%(reset)s "
        "%(log_color)s[%(levelname)s]%(reset)s "
        "%(purple)s[%(name)s]%(reset)s %(message)s"
    )
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setFormatter(
        colorlog.ColoredFormatter(
            log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    # Suppress verbose discord.py noise
    logging.getLogger("discord.gateway").setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
