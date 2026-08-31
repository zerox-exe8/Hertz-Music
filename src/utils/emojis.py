"""
Hertz Music Bot - Emoji Registry
Loads and manages custom emojis for music and UI controls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict
import logging

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Emojis")


class EmojiRegistry:
    """Dynamic Emoji Registry with rich fallbacks."""

    FALLBACKS: Dict[str, str] = {
        "music_playing": "▶️",
        "music_paused": "⏸️",
        "music_stop": "⏹️",
        "music_skip": "⏭️",
        "music_queue": "📜",
        "music_loop": "🔁",
        "music_shuffle": "🔀",
        "music_volume": "🔊",
        "icon_success": "✅",
        "icon_error": "❌",
        "icon_warning": "⚠️",
        "icon_info": "ℹ️"
    }

    def __init__(self, bot: HertzBot) -> None:
        self.bot = bot
        self._emojis: Dict[str, str] = {}

    def get(self, key: str, default: str = "") -> str:
        """Get an emoji by name with fallback."""
        if key in self._emojis:
            return self._emojis[key]
        return self.FALLBACKS.get(key, default)

    async def load(self) -> None:
        """Scan bot's connected guilds for custom emojis."""
        for emoji in self.bot.emojis:
            self._emojis[emoji.name.lower()] = str(emoji)
        logger.info(f"Loaded {len(self._emojis)} custom emojis.")
