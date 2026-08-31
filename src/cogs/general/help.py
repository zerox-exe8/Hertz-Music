"""
Hertz Music Bot - Help Command Module
"""

from __future__ import annotations

import discord
from discord.ext import commands

from src.core.config import Config
from src.core.context import CustomContext


class Help(commands.Cog):
    """Interactive Music Help Menu."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="help", aliases=["h", "commands"], description="Show all available music commands.")
    async def help_command(self, ctx: CustomContext) -> None:
        """Display the complete list of music commands."""
        prefix = Config.DEFAULT_PREFIX

        embed = discord.Embed(
            title=f"🎵 {Config.BOT_NAME} - Music Commands",
            description=f"> {Config.BOT_DESCRIPTION}\n> **Prefix:** `{prefix}` | **Slash Commands:** `/`",
            color=Config.EMBED_COLOR
        )

        music_cmds = (
            f"`{prefix}play <query>` - Play any song in 320kbps master CD quality\n"
            f"`{prefix}pause` - Pause currently playing music\n"
            f"`{prefix}resume` - Resume paused playback\n"
            f"`{prefix}skip` - Skip to next track in queue\n"
            f"`{prefix}stop` - Stop playback, clear queue and leave voice\n"
            f"`{prefix}queue` - Display all upcoming songs in queue\n"
            f"`{prefix}nowplaying` - View details of currently playing track\n"
            f"`{prefix}loop <track/queue/off>` - Toggle song or queue loop\n"
            f"`{prefix}shuffle` - Randomize track order in queue\n"
            f"`{prefix}clear` - Clear all upcoming songs from queue\n"
            f"`{prefix}remove <pos>` - Remove a specific song by its queue position"
        )
        embed.add_field(name="🎶 Music Controls", value=music_cmds, inline=False)

        info_cmds = (
            f"`{prefix}ping` - Check bot latency and voice gateway ping\n"
            f"`{prefix}sync` - Sync slash commands (Developers only)"
        )
        embed.add_field(name="⚙️ Utilities", value=info_cmds, inline=False)

        if Config.SUPPORT_SERVER_URL:
            embed.add_field(name="🔗 Links", value=f"[Support Server]({Config.SUPPORT_SERVER_URL})", inline=False)

        embed.set_footer(text=Config.FOOTER_TEXT)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
