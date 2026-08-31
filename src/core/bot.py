"""
Hertz Music Bot - Core Bot Class
"""

from __future__ import annotations

import logging
from pathlib import Path
import aiohttp
import discord
from discord.ext import commands

from src.core.config import Config
from src.core.context import CustomContext
from src.core.server import HealthServer
from src.utils.emojis import EmojiRegistry

logger = logging.getLogger("Hertz.Core")


class HertzBot(commands.Bot):
    """Dedicated Production-Grade Discord Music Bot."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(Config.DEFAULT_PREFIX),
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
        )

        self.session: aiohttp.ClientSession | None = None
        self.server: HealthServer = HealthServer(self)
        self.custom_emojis: EmojiRegistry = EmojiRegistry(self)

    async def get_context(
        self, origin: discord.Message | discord.Interaction, *, cls: type[CustomContext] = CustomContext
    ) -> CustomContext:
        """Inject our CustomContext into all commands."""
        return await super().get_context(origin, cls=cls)

    async def on_message(self, message: discord.Message) -> None:
        """Central message processor with diagnostics."""
        if message.author.bot:
            return

        if not message.content:
            logger.warning(
                f"Received empty message from {message.author} in #{message.channel}. "
                f"If you typed a command, please ensure 'MESSAGE CONTENT INTENT' is enabled in Discord Developer Portal -> Bot -> Privileged Gateway Intents."
            )
            return

        if message.guild:
            perms = message.channel.permissions_for(message.guild.me)
            logger.info(
                f"Command from {message.author} in #{message.channel.name} ({message.guild.name}) -> '{message.content}' | "
                f"Bot Channel Perms: SendMessages={perms.send_messages}, EmbedLinks={perms.embed_links}, ReadHistory={perms.read_message_history}"
            )
        await self.process_commands(message)

    async def on_ready(self) -> None:
        """Executed when bot is connected and ready."""
        logger.info(f"Connected as {self.user} (ID: {self.user.id if self.user else 'Unknown'})")
        
        # Load emojis from servers
        await self.custom_emojis.load()

        # Set Activity
        activity_type_map = {
            "playing": discord.ActivityType.playing,
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
            "competing": discord.ActivityType.competing,
        }
        act_type = activity_type_map.get(Config.ACTIVITY_TYPE, discord.ActivityType.listening)
        activity = discord.Activity(type=act_type, name=Config.STATUS_TEXT)
        
        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
        }
        status = status_map.get(Config.STATUS_STATE, discord.Status.online)
        await self.change_presence(activity=activity, status=status)
        logger.info(f"Presence set to: {Config.STATUS_TEXT} ({Config.ACTIVITY_TYPE})")
        logger.info(f"Active Guilds: {len(self.guilds)}")
        logger.info(f"Registered Commands: {[c.name for c in self.commands]}")

    async def setup_hook(self) -> None:
        """Asynchronous initialization before websocket login."""
        logger.info("Initializing async subsystems...")
        self.session = aiohttp.ClientSession()

        # Load all Cogs
        await self._load_all_extensions()

        # Start 24/7 Keep-Alive Web Server
        await self.server.start()
        logger.info("Setup hook completed successfully.")

    async def _load_all_extensions(self) -> None:
        """Walk through src/cogs and load every python module."""
        cogs_dir = Path(__file__).resolve().parent.parent / "cogs"

        for file in cogs_dir.rglob("*.py"):
            if any(part.startswith("_") for part in file.parts):
                continue

            relative = file.relative_to(cogs_dir.parent.parent)
            module_name = ".".join(relative.with_suffix("").parts)

            try:
                await self.load_extension(module_name)
                logger.info(f"Loaded extension: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load extension {module_name}: {e}", exc_info=e)

    async def on_command(self, ctx: CustomContext) -> None:
        logger.info(f"==> INVOKING COMMAND: '{ctx.command.name}' from {ctx.author} in #{ctx.channel}")

    async def on_command_completion(self, ctx: CustomContext) -> None:
        logger.info(f"==> SUCCESSFULLY FINISHED: '{ctx.command.name}'")

    async def on_command_error(self, ctx: CustomContext, error: Exception) -> None:
        """Central command error handler."""
        logger.error(f"==> COMMAND ERROR in '{ctx.command}': {error}", exc_info=error)
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing argument: `{error.param.name}`. Use `.help` for usage.")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to use this command.")
            return
        if isinstance(error, commands.CommandInvokeError):
            original = getattr(error, "original", error)
            if isinstance(original, discord.Forbidden):
                await ctx.send("⚠️ Bot is missing permissions (e.g. `Embed Links` or `Connect/Speak`). Please grant Administrator or Embed Links to the bot role.")
                return
            await ctx.send(f"❌ An error occurred: `{original}`")
            return
        await ctx.send(f"❌ Command failed: `{error}`")

    async def close(self) -> None:
        """Gracefully close bot and sessions."""
        if self.session and not self.session.closed:
            await self.session.close()
        await self.server.stop()
        await super().close()
