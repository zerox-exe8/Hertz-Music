"""
Hertz Music Bot - Play Command Handler
"""

from __future__ import annotations

import logging
import shutil
from typing import TYPE_CHECKING
import discord

from src.cogs.music._types import FFMPEG_OPTIONS
from src.cogs.music._resolver import MusicResolver
from src.core.context import CustomContext

if TYPE_CHECKING:
    from src.cogs.music._controller import MusicController

logger = logging.getLogger("Hertz.Music.Cmd.Play")


async def handle_play(ctx: CustomContext, controller: MusicController, query: str) -> None:
    """Execute the play command."""
    logger.info(f"handle_play called with query='{query}', author={ctx.author}")
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("You must be in a Voice Channel to play music.")
        return

    user_channel = ctx.author.voice.channel
    voice_client: discord.VoiceClient = ctx.guild.voice_client

    # 1. Connect or Move Voice Client
    if not voice_client or not voice_client.is_connected():
        try:
            voice_client = await user_channel.connect(self_deaf=True, timeout=20.0, reconnect=True)
        except Exception as e:
            await ctx.send(f"Could not connect to voice channel: `{e}`")
            return
    elif voice_client.channel != user_channel:
        await voice_client.move_to(user_channel)

    status_msg = await ctx.send(f"🔍 Searching for **{query}**...")

    # 2. Resolve Track
    try:
        track = await MusicResolver.resolve(query)
    except Exception as ex:
        logger.error(f"Resolver error for '{query}': {ex}", exc_info=ex)
        await status_msg.edit(content=f"⚠️ Failed to search for **{query}**: `{ex}`")
        return

    if not track or not track.stream_url:
        await status_msg.edit(content=f"No results found for **{query}**.")
        return

    track.requester = ctx.author.display_name
    guild_id = ctx.guild.id
    queue = controller.get_queue(guild_id)

    # 3. Play or Queue Track
    if not voice_client.is_playing() and not voice_client.is_paused():
        controller.current_tracks[guild_id] = track
        try:
            ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"
            source = discord.FFmpegPCMAudio(track.stream_url, executable=ffmpeg_exe, **FFMPEG_OPTIONS)
            voice_client.play(source, after=lambda e: controller._handle_track_finish(ctx, e))

            embed = discord.Embed(
                title="Now Playing",
                description=f"**[{track.title}]({track.url})**\nArtist: `{track.author}`",
                color=0x2B2D31
            )
            if track.thumbnail:
                embed.set_thumbnail(url=track.thumbnail)
            embed.set_footer(text=f"Requested by {track.requester}")

            try:
                await status_msg.edit(content=None, embed=embed)
            except discord.Forbidden:
                await status_msg.edit(content=f"🎶 **Now Playing:** [{track.title}]({track.url}) by `{track.author}` (Requested by {track.requester})")
            except Exception:
                await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error starting playback: {e}", exc_info=e)
            await status_msg.edit(content=f"⚠️ Error playing track: `{e}`")
    else:
        queue.append(track)
        embed = discord.Embed(
            title="Track Queued",
            description=f"**[{track.title}]({track.url})**\nPosition #{len(queue)}",
            color=0x2B2D31
        )
        try:
            await status_msg.edit(content=None, embed=embed)
        except discord.Forbidden:
            await status_msg.edit(content=f"📜 **Track Queued:** [{track.title}]({track.url}) (Position #{len(queue)})")
        except Exception:
            await ctx.send(embed=embed)
