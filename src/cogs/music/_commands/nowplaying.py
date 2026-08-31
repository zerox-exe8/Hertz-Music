"""
Hertz Music Bot - Now Playing Command Handler
"""

from __future__ import annotations

import discord
from src.core.context import CustomContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cogs.music._controller import MusicController


async def handle_nowplaying(ctx: CustomContext, controller: MusicController) -> None:
    """Show details of the currently playing track."""
    guild_id = ctx.guild.id
    current = controller.get_current(guild_id)

    if not current:
        await ctx.send_warning("No track is currently playing.")
        return

    dur_m = current.duration // 60
    dur_s = current.duration % 60

    embed = discord.Embed(
        title="🎵 Now Playing",
        description=f"**[{current.title}]({current.url})**\n\n"
                    f"• **Artist:** `{current.author}`\n"
                    f"• **Duration:** `{dur_m}:{dur_s:02d}`\n"
                    f"• **Requested By:** `{current.requester}`",
        color=0x2B2D31
    )
    if current.thumbnail:
        embed.set_thumbnail(url=current.thumbnail)
    loop_mode = controller.get_loop(guild_id)
    embed.set_footer(text=f"Loop: {loop_mode.upper()} | Hertz Music Engine")
    await ctx.send(embed=embed)
