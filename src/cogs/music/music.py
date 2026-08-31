"""
Hertz Music Bot - Music Cog
Exposes Studio-Grade Music Commands with 100% Exact Matching and Direct Audio Streaming.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.core.context import CustomContext
from src.cogs.music._controller import MusicController
from src.cogs.music._commands.play import handle_play
from src.cogs.music._commands.pause import handle_pause
from src.cogs.music._commands.skip import handle_skip
from src.cogs.music._commands.stop import handle_stop
from src.cogs.music._commands.queue import handle_queue
from src.cogs.music._commands.nowplaying import handle_nowplaying
from src.cogs.music._commands.controls import handle_loop, handle_shuffle, handle_clear

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Music")


class Music(commands.Cog):
    """Studio-Grade Discord Music Engine."""

    def __init__(self, bot: HertzBot) -> None:
        self.bot = bot
        self.controller = MusicController(bot)

    @commands.hybrid_command(name="play", aliases=["p"], description="Play any song in voice channel.")
    @app_commands.describe(query="Song name or link")
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
        voice_client: discord.VoiceClient = ctx.guild.voice_client
        if not voice_client or not voice_client.is_paused():
            await ctx.send("Playback is not paused.")
            return
        voice_client.resume()
        await ctx.send("▶️ Resumed playback.")

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

    @commands.hybrid_command(name="loop", description="Toggle loop mode (off/track/queue).")
    @app_commands.describe(mode="Loop mode: off, track, or queue")
    async def loop(self, ctx: CustomContext, mode: str = "track") -> None:
        """Toggle loop mode."""
        await handle_loop(ctx, self.controller, mode)

    @commands.hybrid_command(name="shuffle", description="Shuffle the current queue.")
    async def shuffle(self, ctx: CustomContext) -> None:
        """Shuffle queue."""
        await handle_shuffle(ctx, self.controller)

    @commands.hybrid_command(name="clear", description="Clear all songs in the queue.")
    async def clear(self, ctx: CustomContext) -> None:
        """Clear queue."""
        await handle_clear(ctx, self.controller)

    @commands.hybrid_command(name="remove", description="Remove a specific song from queue by position.")
    @app_commands.describe(position="Position number of song in queue")
    async def remove(self, ctx: CustomContext, position: int) -> None:
        """Remove a track from queue."""
        from src.cogs.music._commands.controls import handle_remove
        await handle_remove(ctx, self.controller, position)


async def setup(bot: HertzBot) -> None:
    """Load the Music Cog into HertzBot."""
    await bot.add_cog(Music(bot))
