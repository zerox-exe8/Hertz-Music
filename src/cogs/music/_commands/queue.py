"""
Hertz Music Bot - Queue Command Handler
"""

from __future__ import annotations

import discord
from src.core.context import CustomContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cogs.music._controller import MusicController


async def handle_queue(ctx: CustomContext, controller: MusicController) -> None:
    """Show current song queue."""
    guild_id = ctx.guild.id
    current = controller.get_current(guild_id)
    queue = controller.get_queue(guild_id)

    if not current and not queue:
        await ctx.send_warning("The queue is currently empty.")
        return

    lines = []
    if current:
        lines.append(f"**Now Playing:** [{current.title}]({current.url})\nArtist: `{current.author}`\n")
    if queue:
        lines.append(f"**Up Next ({len(queue)} tracks):**")
        for i, t in enumerate(queue[:15], 1):
            dur_m = t.duration // 60
            dur_s = t.duration % 60
            lines.append(f"`{i}.` [{t.title}]({t.url}) - `{dur_m}:{dur_s:02d}` (Req: {t.requester})")
        if len(queue) > 15:
            lines.append(f"\n*...and {len(queue) - 15} more tracks in queue.*")

    embed = discord.Embed(
        title="🎵 Song Queue",
        description="\n".join(lines),
        color=0x2B2D31
    )
    loop_mode = controller.get_loop(guild_id)
    embed.set_footer(text=f"Loop Mode: {loop_mode.upper()} | Total Tracks: {len(queue) + (1 if current else 0)}")
    await ctx.send(embed=embed)
