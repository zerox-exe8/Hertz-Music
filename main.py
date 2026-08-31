"""
Hertz Music Bot - Main Entrypoint
"""

import asyncio
import logging
import colorlog

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

from src.core.config import Config
from src.core.bot import HertzBot


def setup_logging() -> None:
    """Setup structured colorized console logging."""
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] [%(name)s]%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


async def main() -> None:
    setup_logging()
    logger = logging.getLogger("Hertz.Main")

    if not Config.DISCORD_TOKEN:
        logger.critical("DISCORD_TOKEN is missing in .env! Please set your bot token and restart.")
        return

    bot = HertzBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nHertz Music Bot shutdown requested.")
