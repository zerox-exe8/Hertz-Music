"""
Hertz Music Bot - Wavelink & Lavalink Music Engine
Connects directly to the dedicated 24/7 Lavalink node for high-performance audio playback.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, cast

import discord
from discord import app_commands
from discord.ext import commands
import wavelink

from src.core.config import Config
from src.core.context import CustomContext
from src.cogs.music._resolver import MusicResolver

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Music")


class Music(commands.Cog):
    """Studio-Grade Discord Music Engine Powered by Lavalink & Wavelink."""

    def __init__(self, bot: HertzBot) -> None:
        self.bot = bot
        self._node_task = asyncio.create_task(self._ensure_node())

    async def _ensure_node(self) -> bool:
        """Connect to Lavalink Node."""
        for n in wavelink.Pool.nodes.values():
            if n.status == wavelink.NodeStatus.CONNECTED:
                return True

        uri = Config.LAVALINK_URI
        password = Config.LAVALINK_PASSWORD
        if not uri:
            return False

        for attempt in range(5):
            try:
                node = wavelink.Node(uri=uri, password=password)
                await wavelink.Pool.connect(nodes=[node], client=self.bot)
                for _ in range(25):
                    for n in wavelink.Pool.nodes.values():
                        if n.status == wavelink.NodeStatus.CONNECTED:
                            logger.info(f"Successfully connected to Lavalink Node at {uri}")
                            return True
                    await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Failed to connect to Lavalink node: {e}")
                return False
        return False

    @commands.hybrid_command(name="play", aliases=["p"], description="Play any song in voice channel.")
    @app_commands.describe(query="Song name or link")
    async def play(self, ctx: CustomContext, *, query: str) -> None:
        """Play music tracks in voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You must be in a Voice Channel to play music.")
            return

        if not await self._ensure_node():
            await ctx.send("Audio server is initializing, please try again in 5 seconds.")
            return

        user_channel = ctx.author.voice.channel

        # 1. Connect Voice Client with Wavelink Player
        player: wavelink.Player | None = cast(wavelink.Player, ctx.guild.voice_client)
        if not player or not player.connected:
            try:
                player = await user_channel.connect(cls=wavelink.Player, self_deaf=True)
            except Exception as e:
                await ctx.send(f"Could not connect to voice channel: `{e}`")
                return
        elif player.channel != user_channel:
            await player.move_to(user_channel)

        status_msg = await ctx.send(f"Searching for **{query}**...")
        
        track = None
        clean_q = query.strip()

        # 1. Primary: Deezer Studio Audio via LavaSrc
        try:
            dz_res = await wavelink.Playable.search(f"dzsearch:{clean_q}")
            if dz_res:
                track = dz_res[0] if isinstance(dz_res, list) else dz_res
        except Exception:
            track = None

        # 2. Secondary: 320kbps CD Master Stream via Direct Resolver
        if not track:
            try:
                resolved = await MusicResolver.resolve(query)
                if resolved and resolved.stream_url:
                    search_res = await wavelink.Playable.search(resolved.stream_url)
                    if search_res:
                        track = search_res[0] if isinstance(search_res, list) else search_res
                        if resolved.title:
                            track._title = resolved.title
                        if resolved.author:
                            track._author = resolved.author
                        if resolved.thumbnail:
                            track._artwork = resolved.thumbnail
            except Exception as e:
                logger.warning(f"Direct stream resolve notice: {e}")
                track = None

        # 3. Direct Audio URL / YouTube Fallback
        if not track:
            try:
                search_res = await wavelink.Playable.search(clean_q)
                if search_res:
                    track = search_res[0] if isinstance(search_res, list) else search_res
            except Exception:
                track = None

        if not track:
            await status_msg.edit(content=f"No results found for **{query}**.")
            return

        # 4. Play Track or Queue
        if not player.playing:
            await player.set_volume(100)
            await player.play(track, volume=100, paused=False)
            embed = discord.Embed(
                title="Now Playing",
                description=f"**[{track.title}]({track.uri})**\nArtist: `{track.author}`",
                color=0x2B2D31
            )
            if getattr(track, "artwork", None):
                embed.set_thumbnail(url=track.artwork)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            try:
                await status_msg.edit(content=None, embed=embed)
            except discord.Forbidden:
                await status_msg.edit(content=f"🎶 **Now Playing:** [{track.title}]({track.uri}) by `{track.author}`")
        else:
            await player.queue.put_wait(track)
            embed = discord.Embed(
                title="Track Queued",
                description=f"**[{track.title}]({track.uri})**\nPosition #{player.queue.count}",
                color=0x2B2D31
            )
            try:
                await status_msg.edit(content=None, embed=embed)
            except discord.Forbidden:
                await status_msg.edit(content=f"📜 **Track Queued:** [{track.title}]({track.uri}) (Position #{player.queue.count})")

    @commands.hybrid_command(name="pause", description="Pause currently playing music.")
    async def pause(self, ctx: CustomContext) -> None:
        """Pause playback."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player or not player.playing:
            await ctx.send("No music is currently playing.")
            return
        await player.pause(True)
        await ctx.send("Playback paused.")

    @commands.hybrid_command(name="resume", aliases=["unpause"], description="Resume paused music.")
    async def resume(self, ctx: CustomContext) -> None:
        """Resume playback."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.send("I am not connected to a voice channel.")
            return
        await player.pause(False)
        await ctx.send("Playback resumed.")

    @commands.hybrid_command(name="skip", aliases=["s", "next"], description="Skip the current track.")
    async def skip(self, ctx: CustomContext) -> None:
        """Skip currently playing track."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player or not player.playing:
            await ctx.send("No track is currently playing.")
            return
        await player.skip(force=True)
        await ctx.send("Skipped to next track.")

    @commands.hybrid_command(name="stop", aliases=["disconnect", "dc"], description="Stop playback and leave voice.")
    async def stop(self, ctx: CustomContext) -> None:
        """Stop music, clear queue and leave voice."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player:
            await ctx.send("I am not connected to a voice channel.")
            return
        player.queue.clear()
        await player.disconnect()
        await ctx.send("Stopped playback and disconnected.")

    @commands.hybrid_command(name="queue", aliases=["q"], description="Show song queue.")
    async def queue(self, ctx: CustomContext) -> None:
        """Show current song queue."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player or (not player.current and player.queue.is_empty):
            await ctx.send("The queue is empty.")
            return
        lines = []
        if player.current:
            lines.append(f"**Now Playing:** {player.current.title}")
        if not player.queue.is_empty:
            lines.append("\n**Up Next:**")
            for i, t in enumerate(list(player.queue)[:10], 1):
                lines.append(f"`{i}.` {t.title}")
        await ctx.send("\n".join(lines))

    @commands.hybrid_command(name="nowplaying", aliases=["np"], description="Show currently playing song.")
    async def nowplaying(self, ctx: CustomContext) -> None:
        """Show currently playing song details."""
        player: wavelink.Player = cast(wavelink.Player, ctx.guild.voice_client)
        if not player or not player.current:
            await ctx.send("No track is currently playing.")
            return

        embed = discord.Embed(
            title="Now Playing",
            description=f"**[{player.current.title}]({player.current.uri})**\nArtist: `{player.current.author}`",
            color=0x2B2D31
        )
        if getattr(player.current, "artwork", None):
            embed.set_thumbnail(url=player.current.artwork)
        embed.set_footer(text=f"Volume: {player.volume}%")
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"🎶 **Now Playing:** [{player.current.title}]({player.current.uri}) by `{player.current.author}`")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        """Advance queue on track end."""
        player: wavelink.Player = payload.player
        reason_str = str(getattr(payload, "reason", "")).lower()
        if "replaced" in reason_str:
            return
        if not player.queue.is_empty:
            next_track = await player.queue.get_wait()
            await player.play(next_track, volume=100, paused=False)


async def setup(bot: HertzBot) -> None:
    """Load the Music Cog into HertzBot."""
    await bot.add_cog(Music(bot))
