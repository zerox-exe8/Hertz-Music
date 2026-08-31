"""
Hertz Music Bot - Slash Command Sync Tool
"""

from __future__ import annotations

import discord
from discord.ext import commands

from src.core.config import Config
from src.core.context import CustomContext


class Sync(commands.Cog):
    """Developer Slash Command Synchronization."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="sync", description="Sync slash commands to Discord.")
    async def sync_commands(self, ctx: CustomContext, spec: str = "global") -> None:
        """Sync slash application commands."""
        # Developer check
        if ctx.author.id not in Config.DEVELOPER_IDS and ctx.author.id != (await self.bot.application_info()).owner.id:
            await ctx.send_error("You do not have permission to sync slash commands.")
            return

        msg = await ctx.send("🔄 Synchronizing application commands with Discord...")
        if spec == "guild" and ctx.guild:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await msg.edit(content=f"✅ Synced **{len(synced)}** slash commands to this server (`{ctx.guild.name}`).")
        else:
            synced = await self.bot.tree.sync()
            await msg.edit(content=f"✅ Synced **{len(synced)}** slash commands globally.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Sync(bot))
