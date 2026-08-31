"""
Hertz Music Bot - Main Entrypoint
"""

from __future__ import annotations

import asyncio
import os
import sys

from src.utils.logger import setup_logging
setup_logging()

import static_ffmpeg
import discord.opus

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
                print(f"Error loading {dll_name}: {e}")

from src.core.bot import HertzBot
from src.core.config import Config


async def main() -> None:
    bot = HertzBot()
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
