"""
Hertz Music Bot - Loop, Shuffle, Clear & Remove Handlers
"""

from __future__ import annotations

import random
import discord
from src.core.context import CustomContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cogs.music._controller import MusicController


async def handle_loop(ctx: CustomContext, controller: MusicController, mode: str = "track") -> None:
    """Toggle track or queue loop mode."""
    guild_id = ctx.guild.id
    mode_clean = mode.lower().strip()

    if mode_clean in ["track", "song", "1"]:
        controller.set_loop(guild_id, "track")
        await ctx.send_success("Loop set to **Single Track** 🔂.")
    elif mode_clean in ["queue", "all"]:
        controller.set_loop(guild_id, "queue")
        await ctx.send_success("Loop set to **Entire Queue** 🔁.")
    elif mode_clean in ["off", "disable", "stop"]:
        controller.set_loop(guild_id, "off")
        await ctx.send_success("Loop mode **Disabled**.")
    else:
        # Toggle cycle: off -> track -> queue -> off
        current = controller.get_loop(guild_id)
        next_mode = "track" if current == "off" else ("queue" if current == "track" else "off")
        controller.set_loop(guild_id, next_mode)
        await ctx.send_success(f"Loop mode toggled to **{next_mode.upper()}**.")


async def handle_shuffle(ctx: CustomContext, controller: MusicController) -> None:
    """Shuffle the current song queue."""
    guild_id = ctx.guild.id
    queue = controller.get_queue(guild_id)

    if len(queue) < 2:
        await ctx.send_warning("Queue needs at least 2 tracks to shuffle.")
        return

    random.shuffle(queue)
    await ctx.send_success(f"Shuffled **{len(queue)}** tracks in queue 🔀.")


async def handle_clear(ctx: CustomContext, controller: MusicController) -> None:
    """Clear all upcoming songs from queue."""
    guild_id = ctx.guild.id
    queue = controller.get_queue(guild_id)

    if not queue:
        await ctx.send_warning("The queue is already empty.")
        return

    count = len(queue)
    queue.clear()
    await ctx.send_success(f"Cleared **{count}** tracks from queue.")


async def handle_remove(ctx: CustomContext, controller: MusicController, position: int) -> None:
    """Remove a specific track from queue by its position number."""
    guild_id = ctx.guild.id
    queue = controller.get_queue(guild_id)

    if not queue:
        await ctx.send_warning("The queue is empty.")
        return

    if position < 1 or position > len(queue):
        await ctx.send_warning(f"Invalid position. Please specify a number between 1 and {len(queue)}.")
        return

    removed = queue.pop(position - 1)
    await ctx.send_success(f"Removed **[{removed.title}]({removed.url})** from queue.")
