"""
Hertz Music Bot - Main Entrypoint
With Unbreakable Rate-Limit Auto-Retry and Crash Prevention.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from src.utils.logger import setup_logging
setup_logging()

import static_ffmpeg
import discord
import discord.opus

logger = logging.getLogger("Hertz.Main")

# Ensure FFmpeg binaries are registered on PATH
static_ffmpeg.add_paths()

# Ensure Opus DLL is loaded on Windows
if not discord.opus.is_loaded():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for dll_name in ["opus.dll", "libopus-0.dll", "libopus.dll"]:
        dll_path = os.path.join(base_dir, dll_name)
        if os.path.exists(dll_path):
            try:
                discord.opus.load_opus(dll_path)
                break
            except Exception as e:
                logger.warning(f"Notice loading {dll_name}: {e}")

from src.core.bot import HertzBot
from src.core.config import Config


async def run_bot() -> None:
    """Run bot with auto-reconnect on rate limits or network glitches."""
    if not Config.DISCORD_TOKEN:
        logger.critical("FATAL: DISCORD_TOKEN is missing! Please set DISCORD_TOKEN in Render Environment Variables.")
        sys.exit(1)

    while True:
        try:
            bot = HertzBot()
            async with bot:
                await bot.start(Config.DISCORD_TOKEN)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, "retry_after", 30) or 30
                logger.warning(f"Discord 429 Rate Limit encountered. Waiting {retry_after}s before retrying...")
                await asyncio.sleep(float(retry_after) + 2.0)
            else:
                logger.error(f"Discord HTTP Exception: {e}. Retrying in 15s...")
                await asyncio.sleep(15)
        except discord.LoginFailure as e:
            logger.critical(f"FATAL: Discord Login Failure (Invalid Token): {e}")
            break
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Bot execution cancelled.")
            break
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}. Retrying in 10s...", exc_info=e)
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
