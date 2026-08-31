"""
Hertz Music Bot - Main Entrypoint
Production Cloud Engine with 24/7 Web Server and Resilient Rate-Limit Backoff.
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
from src.core.server import HealthServer

active_bot: HertzBot | None = None


def get_current_bot() -> HertzBot | None:
    return active_bot


async def run_bot_loop() -> None:
    """Run bot with smart exponential backoff for Cloudflare / Discord 429 rate limits."""
    global active_bot

    if not Config.DISCORD_TOKEN:
        logger.critical("FATAL: DISCORD_TOKEN is missing! Please set DISCORD_TOKEN in Render Environment Variables.")
        return

    delay = 15.0

    while True:
        try:
            bot = HertzBot()
            active_bot = bot
            logger.info("Connecting to Discord Gateway...")
            async with bot:
                await bot.start(Config.DISCORD_TOKEN)
            # If start exited cleanly without exception, wait before potential reconnect
            delay = 15.0
            await asyncio.sleep(5)
        except discord.HTTPException as e:
            if e.status == 429:
                logger.warning(f"Discord 429 Rate Limit encountered. Cooling down for {delay:.0f}s before retrying...")
                await asyncio.sleep(delay)
                delay = min(delay * 2.0, 300.0)
            else:
                logger.error(f"Discord HTTP Exception ({e.status}): {e}. Retrying in 15s...")
                await asyncio.sleep(15)
        except discord.LoginFailure as e:
            logger.critical(f"FATAL: Discord Login Failure (Invalid Token): {e}")
            break
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Bot execution cancelled.")
            break
        except Exception as e:
            logger.error(f"Connection glitch: {e}. Retrying in 10s...", exc_info=e)
            await asyncio.sleep(10)
        finally:
            active_bot = None


async def main() -> None:
    # 1. Start 24/7 Keep-Alive Web Server immediately for Render Health Checks
    server = HealthServer(bot_getter=get_current_bot)
    await server.start()

    # 2. Run the Discord Bot Connection Loop
    try:
        await run_bot_loop()
    finally:
        await server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
