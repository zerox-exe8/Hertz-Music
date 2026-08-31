"""
Hertz Music Bot - Music Cog Entrypoint
Aggregates all modular commands and connects them to the central controller.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from src.cogs.music._controller import MusicController
from src.cogs.music._commands.play import handle_play
from src.cogs.music._commands.pause import handle_pause, handle_resume
from src.cogs.music._commands.skip import handle_skip
from src.cogs.music._commands.stop import handle_stop
from src.cogs.music._commands.queue import handle_queue
from src.cogs.music._commands.nowplaying import handle_nowplaying
from src.cogs.music._commands.controls import (
    handle_loop,
    handle_shuffle,
    handle_clear,
    handle_remove
)
from src.core.context import CustomContext

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Music")


class Music(commands.Cog):
    """Studio-Grade 320kbps Lossless Discord Music Engine."""

    def __init__(self, bot: HertzBot) -> None:
        self.bot = bot
        self.controller = MusicController(bot)

    @commands.hybrid_command(name="play", aliases=["p"], description="Play any song in voice channel.")
    @app_commands.describe(query="Song name, YouTube URL, or Spotify link")
    async def play(self, ctx: CustomContext, *, query: str) -> None:
        """Play exact music tracks in voice channel."""
        await handle_play(ctx, self.controller, query)

    @commands.hybrid_command(name="pause", description="Pause currently playing music.")
    async def pause(self, ctx: CustomContext) -> None:
        """Pause playback."""
        await handle_pause(ctx, self.controller)

    @commands.hybrid_command(name="resume", aliases=["unpause"], description="Resume paused music.")
    async def resume(self, ctx: CustomContext) -> None:
        """Resume playback."""
        await handle_resume(ctx, self.controller)

    @commands.hybrid_command(name="skip", aliases=["s", "next"], description="Skip the current track.")
    async def skip(self, ctx: CustomContext) -> None:
        """Skip currently playing track."""
        await handle_skip(ctx, self.controller)

    @commands.hybrid_command(name="stop", aliases=["disconnect", "dc"], description="Stop playback and leave voice.")
    async def stop(self, ctx: CustomContext) -> None:
        """Stop music, clear queue and leave voice."""
        await handle_stop(ctx, self.controller)

    @commands.hybrid_command(name="queue", aliases=["q"], description="Show song queue.")
    async def queue(self, ctx: CustomContext) -> None:
        """Show current song queue."""
        await handle_queue(ctx, self.controller)

    @commands.hybrid_command(name="nowplaying", aliases=["np"], description="Show currently playing song.")
    async def nowplaying(self, ctx: CustomContext) -> None:
        """Show currently playing song details."""
        await handle_nowplaying(ctx, self.controller)

    @commands.hybrid_command(name="loop", description="Toggle loop mode (track, queue, off).")
    @app_commands.describe(mode="Loop mode: 'track', 'queue', or 'off'")
    async def loop(self, ctx: CustomContext, mode: str = "track") -> None:
        """Set track or queue loop mode."""
        await handle_loop(ctx, self.controller, mode)

    @commands.hybrid_command(name="shuffle", description="Shuffle all upcoming songs in the queue.")
    async def shuffle(self, ctx: CustomContext) -> None:
        """Shuffle queue."""
        await handle_shuffle(ctx, self.controller)

    @commands.hybrid_command(name="clear", description="Clear all songs from the queue.")
    async def clear(self, ctx: CustomContext) -> None:
        """Clear queue."""
        await handle_clear(ctx, self.controller)

    @commands.hybrid_command(name="remove", description="Remove a specific song from queue by position number.")
    @app_commands.describe(position="Position number of the song in the queue (e.g. 1, 2, 3)")
    async def remove(self, ctx: CustomContext, position: int) -> None:
        """Remove a song from queue."""
        await handle_remove(ctx, self.controller, position)


async def setup(bot: HertzBot) -> None:
    """Load the Music Cog into HertzBot."""
    await bot.add_cog(Music(bot))
