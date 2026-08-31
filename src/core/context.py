"""
Hertz Music Bot - Custom Command Context
"""

from __future__ import annotations

from typing import Any, Optional
import discord
from discord.ext import commands

from src.utils.containers import MusicContainer, send_container_response


class CustomContext(commands.Context):
    """Custom context providing convenient helper response methods."""

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
