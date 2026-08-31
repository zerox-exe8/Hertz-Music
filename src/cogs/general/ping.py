"""
Hertz Music Bot - Ping Command Module
"""

from __future__ import annotations

import time
import discord
from discord.ext import commands

from src.core.context import CustomContext
from src.core.config import Config


class Ping(commands.Cog):
    """Latency and Voice Diagnostics."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check bot latency and voice gateway response time.")
    async def ping_command(self, ctx: CustomContext) -> None:
        """Check websocket and REST API latency."""
        t0 = time.perf_counter()
        msg = await ctx.send("Measuring latency...")
        t1 = time.perf_counter()

        rest_latency = round((t1 - t0) * 1000, 2)
        ws_latency = round(self.bot.latency * 1000, 2)

        voice_latency_str = "Not Connected"
        if ctx.guild and ctx.guild.voice_client:
            voice_latency_str = f"{round(ctx.guild.voice_client.latency * 1000, 2)} ms"

        plain_text = f"**Pong!**\n• WebSocket: `{ws_latency} ms`\n• REST API: `{rest_latency} ms`\n• Voice Gateway: `{voice_latency_str}`"

        embed = discord.Embed(
            title="Pong!",
            color=Config.EMBED_COLOR
        )
        embed.add_field(name="WebSocket", value=f"`{ws_latency} ms`", inline=True)
        embed.add_field(name="REST API", value=f"`{rest_latency} ms`", inline=True)
        embed.add_field(name="Voice Gateway", value=f"`{voice_latency_str}`", inline=True)
        embed.set_footer(text=Config.FOOTER_TEXT)

        try:
            await msg.edit(content=None, embed=embed)
        except discord.Forbidden:
            await msg.edit(content=plain_text)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
