"""
Hertz Music Bot - Custom Command Context
Includes automatic plain-text fallback when Discord 'Embed Links' permission is missing.
"""

from __future__ import annotations

from typing import Any, Optional
import discord
from discord.ext import commands

from src.utils.containers import MusicContainer, send_container_response


class CustomContext(commands.Context):
    """Custom context providing convenient helper response methods."""

    async def send(self, content: Optional[str] = None, *, embed: Optional[discord.Embed] = None, **kwargs) -> discord.Message:
        """Safe send with automatic fallback for missing embed permissions."""
        try:
            return await super().send(content, embed=embed, **kwargs)
        except discord.Forbidden:
            if embed:
                # Convert embed to clean plain text fallback
                parts = []
                if embed.title:
                    parts.append(f"**{embed.title}**")
                if embed.description:
                    parts.append(embed.description)
                for field in embed.fields:
                    parts.append(f"\n**{field.name}**\n{field.value}")
                if embed.footer and embed.footer.text:
                    parts.append(f"\n_{embed.footer.text}_")
                fallback_text = "\n".join(parts)
                final_content = f"{content}\n{fallback_text}" if content else fallback_text
                return await super().send(final_content, **kwargs)
            raise

    async def send_container(
        self,
        container: MusicContainer,
        ephemeral: bool = False
    ) -> Optional[discord.Message]:
        """Send formatted container."""
        if self.interaction:
            return await send_container_response(self.interaction, container, ephemeral=ephemeral)
        return await send_container_response(self.message, container, ephemeral=ephemeral)

    async def send_success(
        self,
        message: str,
        title: str = "Success",
        ephemeral: bool = False
    ) -> Any:
        """Send formatted success card."""
        e_reg = getattr(self.bot, "custom_emojis", None)
        icon = e_reg.get("icon_success", "✅") if e_reg else "✅"

        container = MusicContainer(title=f"{icon} {title}")
        container.add_text(message)
        container.set_footer(f"Requested by {self.author.display_name}")
        return await self.send_container(container, ephemeral=ephemeral)

    async def send_error(
        self,
        message: str,
        title: str = "Error",
        ephemeral: bool = True
    ) -> Any:
        """Send formatted error card."""
        e_reg = getattr(self.bot, "custom_emojis", None)
        icon = e_reg.get("icon_error", "❌") if e_reg else "❌"

        container = MusicContainer(title=f"{icon} {title}")
        container.add_text(message)
        container.set_footer(f"Requested by {self.author.display_name}")
        return await self.send_container(container, ephemeral=ephemeral)

    async def send_warning(
        self,
        message: str,
        title: str = "Warning",
        ephemeral: bool = False
    ) -> Any:
        """Send formatted warning card."""
        e_reg = getattr(self.bot, "custom_emojis", None)
        icon = e_reg.get("icon_warning", "⚠️") if e_reg else "⚠️"

        container = MusicContainer(title=f"{icon} {title}")
        container.add_text(message)
        container.set_footer(f"Requested by {self.author.display_name}")
        return await self.send_container(container, ephemeral=ephemeral)
