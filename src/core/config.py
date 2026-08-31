"""
Hertz Music Bot - Configuration Module
Fully dynamic environment variable reader.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Dynamic configuration container for Hertz Music Bot."""

    # Discord Bot Token
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "").strip()

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()

    # Lavalink Node Configuration
    LAVALINK_URI: str = os.getenv("LAVALINK_URI", "http://fi15.bot-hosting.net:26267").strip()
    LAVALINK_PASSWORD: str = os.getenv("LAVALINK_PASSWORD", "NfJXUsGSO4tVI1LDl7v3XPYZ").strip()

    # Bot Identity & Branding
    BOT_NAME: str = os.getenv("BOT_NAME", "Hertz Music").strip()
    BOT_DESCRIPTION: str = os.getenv("BOT_DESCRIPTION", "Next-Gen Discord Music Bot").strip()
    DEFAULT_PREFIX: str = os.getenv("DEFAULT_PREFIX", ".").strip()
    FOOTER_TEXT: str = os.getenv("FOOTER_TEXT", "Hertz Music").strip()

    # Color Settings
    try:
        EMBED_COLOR: int = int(os.getenv("EMBED_COLOR", "0x2B2D31"), 16)
    except ValueError:
        EMBED_COLOR: int = 0x2B2D31

    # Presence & Status
    STATUS_TEXT: str = os.getenv("STATUS_TEXT", ".help | Play Music").strip()
    ACTIVITY_TYPE: str = os.getenv("ACTIVITY_TYPE", "listening").strip().lower()
    STATUS_STATE: str = os.getenv("STATUS_STATE", "online").strip().lower()

    # Links
    SUPPORT_SERVER_URL: str = os.getenv("SUPPORT_SERVER_URL", "https://discord.gg/").strip()
    BOT_INVITE_URL: str = os.getenv("BOT_INVITE_URL", "").strip()

    # Developers
    _raw_devs: str = os.getenv("DEVELOPER_IDS", "").strip()
    DEVELOPER_IDS: list[int] = [int(i.strip()) for i in _raw_devs.split(",") if i.strip().isdigit()]

    # Web Server Port
    PORT: int = int(os.getenv("PORT", "8080"))
