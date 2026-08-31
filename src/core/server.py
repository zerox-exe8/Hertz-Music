"""
Hertz Music Bot - 24/7 Keep-Alive Web Server
Provides health check endpoints for cloud platforms (Render, Railway, UptimeRobot).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from aiohttp import web

from src.core.config import Config

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Server")


class HealthServer:
    """Lightweight 24/7 HTTP server for status and uptime monitors."""

    def __init__(self, bot: HertzBot) -> None:
        self.bot = bot
        self.app = web.Application()
        self.runner: web.AppRunner | None = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/health", self._handle_health)

    async def _handle_index(self, request: web.Request) -> web.Response:
        guilds = len(self.bot.guilds) if self.bot.is_ready() else 0
        users = len(self.bot.users) if self.bot.is_ready() else 0
        html = (
            f"<html><head><title>{Config.BOT_NAME} Status</title></head>"
            f"<body style='font-family:sans-serif;background:#18191c;color:#fff;padding:40px;text-align:center;'>"
            f"<h1>🎵 {Config.BOT_NAME} is Online!</h1>"
            f"<p>{Config.BOT_DESCRIPTION}</p>"
            f"<p>Serving <b>{guilds}</b> servers and <b>{users}</b> listeners.</p>"
            f"</body></html>"
        )
        return web.Response(text=html, content_type="text/html")

    async def _handle_health(self, request: web.Request) -> web.Response:
        return web.json_response({
            "status": "healthy",
            "bot": Config.BOT_NAME,
            "latency": round(self.bot.latency * 1000, 2) if self.bot.is_ready() else None
        })

    async def start(self) -> None:
        """Start the web server."""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", Config.PORT)
        await site.start()
        logger.info(f"24/7 Keep-Alive Web Server started on port {Config.PORT}")

    async def stop(self) -> None:
        """Stop the web server."""
        if self.runner:
            await self.runner.cleanup()
