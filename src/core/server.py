"""
Hertz Music Bot - 24/7 Keep-Alive Web Server
Provides health check endpoints for cloud platforms (Render, Railway, UptimeRobot).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional, Callable
from aiohttp import web

from src.core.config import Config

if TYPE_CHECKING:
    from src.core.bot import HertzBot

logger = logging.getLogger("Hertz.Server")


class HealthServer:
    """Lightweight 24/7 HTTP server for status and uptime monitors."""

    def __init__(self, bot_getter: Optional[Callable[[], Optional[HertzBot]]] = None) -> None:
        self.bot_getter = bot_getter
        self.app = web.Application()
        self.runner: web.AppRunner | None = None
        self._setup_routes()

    def _setup_routes(self) -> None:
        self.app.router.add_get("/", self._handle_index)
        self.app.router.add_get("/health", self._handle_health)

    def _get_bot(self) -> Optional[HertzBot]:
        if self.bot_getter:
            return self.bot_getter()
        return None

    async def _handle_index(self, request: web.Request) -> web.Response:
        bot = self._get_bot()
        guilds = len(bot.guilds) if bot and bot.is_ready() else 0
        users = len(bot.users) if bot and bot.is_ready() else 0
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
        bot = self._get_bot()
        return web.json_response({
            "status": "healthy",
            "bot": Config.BOT_NAME,
            "connected": bot.is_ready() if bot else False,
            "latency": round(bot.latency * 1000, 2) if bot and bot.is_ready() else None
        })

    async def start(self) -> None:
        """Start the web server safely."""
        if self.runner is not None:
            return
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            site = web.TCPSite(self.runner, "0.0.0.0", Config.PORT)
            await site.start()
            logger.info(f"24/7 Keep-Alive Web Server started on port {Config.PORT}")
        except Exception as e:
            logger.error(f"Error starting web server on port {Config.PORT}: {e}")

    async def stop(self) -> None:
        """Stop the web server."""
        if self.runner:
            try:
                await self.runner.cleanup()
            except Exception:
                pass
            self.runner = None
