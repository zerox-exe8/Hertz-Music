"""
Hertz Music Bot - Card Container UI Formatter
"""

from __future__ import annotations

from typing import Optional, Union
import discord
from src.core.config import Config


class MusicContainer:
    """Rich Embed Container for music responses."""

    def __init__(self, title: Optional[str] = None, accent_color: Optional[int] = None) -> None:
        self.title = title
        self.color = accent_color if accent_color is not None else Config.EMBED_COLOR
        self.description_parts: list[str] = []
        self.thumbnail_url: Optional[str] = None
        self.footer_text: Optional[str] = None

    def add_text(self, text: str) -> MusicContainer:
        self.description_parts.append(text)
        return self

    def add_separator(self, divider: bool = True) -> MusicContainer:
        if divider:
            self.description_parts.append("---")
        return self

    def set_thumbnail(self, url: str) -> MusicContainer:
        self.thumbnail_url = url
        return self

    def set_footer(self, text: str) -> MusicContainer:
        self.footer_text = text
        return self

    def build(self) -> discord.Embed:
        embed = discord.Embed(
            title=self.title,
            description="\n".join(self.description_parts),
            color=self.color
        )
        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)
        footer = self.footer_text or Config.FOOTER_TEXT
        embed.set_footer(text=footer)
        return embed


async def send_container_response(
    target: Union[discord.Message, discord.Interaction],
    container: MusicContainer,
    ephemeral: bool = False
) -> Optional[discord.Message]:
    """Send formatted container embed response with automatic text fallback."""
    embed = container.build()
    plain_text = f"**{container.title or ''}**\n\n" + "\n".join(container.description_parts)
    try:
        if isinstance(target, discord.Interaction):
            if target.response.is_done():
                return await target.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await target.response.send_message(embed=embed, ephemeral=ephemeral)
                return None
        elif isinstance(target, discord.Message):
            return await target.reply(embed=embed, mention_author=False)
    except discord.Forbidden:
        # Fallback if bot lacks 'Embed Links' permission
        if isinstance(target, discord.Interaction):
            if target.response.is_done():
                return await target.followup.send(content=plain_text, ephemeral=ephemeral)
            else:
                await target.response.send_message(content=plain_text, ephemeral=ephemeral)
                return None
        elif isinstance(target, discord.Message):
            return await target.reply(content=plain_text, mention_author=False)
    return None
