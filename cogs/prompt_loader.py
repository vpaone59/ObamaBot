import os
from typing import Optional

import discord
import httpx
from discord import app_commands
from discord.ext import commands, tasks

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)


class PromptManager:
    def __init__(self, api_url: Optional[str], timeout: int = 10):
        self.api_url = api_url
        self.timeout = timeout
        self.prompt: Optional[str] = None
        self.updated_at: Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def fetch_prompt(self) -> bool:
        """Fetch the active prompt from the configured API. Returns True on success."""
        if not self.api_url:
            logger.debug("Prompt API URL not configured")
            return False
        # support configuring either the full endpoint or the base URL
        if self.api_url.rstrip().endswith("/bot-prompt/current"):
            url = self.api_url
        else:
            url = self.api_url.rstrip("/") + "/bot-prompt/current"

        client = await self._get_client()

        try:
            # Django API does not require auth; fetch without Authorization header
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            # ninja returns null when not found; handle that
            if not data:
                logger.info("No active bot prompt returned from API")
                self.prompt = None
                self.updated_at = None
                return False
            self.prompt = data.get("prompt")
            self.updated_at = data.get("updated_at")
            logger.info("Loaded bot prompt (updated: %s)", self.updated_at)
            return True
        except Exception as e:
            logger.warning("Failed to load bot prompt: %s", e)
            return False

    async def close(self):
        if self._client:
            await self._client.aclose()


class PromptLoader(commands.Cog):
    """Cog that manages loading the system prompt from a webapp API and refreshing it."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        api_url = os.getenv("BOT_PROMPT_API_URL")
        self.manager = PromptManager(api_url=api_url)
        # do not start background tasks here; start in cog_load
        # attach to bot in cog_load for other cogs to access

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    async def cog_load(self):
        """Initialize background task and attach manager to bot when cog loads."""
        setattr(self.bot, "prompt_manager", self.manager)
        try:
            self.refresh_prompt.start()
        except RuntimeError:
            # already started or event loop issue
            logger.debug("refresh_prompt task already started or failed to start")

        # register app command for showing the prompt
        show_cmd = app_commands.Command(
            name="show_prompt",
            description="Show current bot AI system prompt",
            callback=self._show_prompt_app,
        )
        try:
            # Register command as a guild command for each guild the bot is currently in
            # so guild syncs will include it immediately. Avoid global sync here.
            if self.bot.guilds:
                for g in self.bot.guilds:
                    try:
                        self.bot.tree.add_command(
                            show_cmd, guild=discord.Object(id=g.id)
                        )
                    except Exception as e:
                        logger.debug(
                            "Failed to add show_prompt to guild %s: %s", g.id, e
                        )
                logger.debug(
                    "Registered show_prompt app command for %d guild(s)",
                    len(self.bot.guilds),
                )
            else:
                # fallback: add without guild (global) and rely on manual global sync
                self.bot.tree.add_command(show_cmd)
                logger.debug("Registered show_prompt app command globally (not synced)")
        except Exception as e:
            logger.warning("Failed to register app command show_prompt: %s", e)

    async def cog_unload(self):
        """Cancel background task and close HTTP client when cog unloads."""
        try:
            self.refresh_prompt.cancel()
        except Exception:
            pass

        try:
            await self.manager.close()
        except Exception:
            logger.debug("Failed to close PromptManager client on unload")

    async def _show_prompt_app(self, interaction: discord.Interaction):
        """App command handler to display current prompt."""
        logger.info(
            "/show_prompt invoked by %s in guild %s",
            interaction.user,
            getattr(interaction.guild, "id", None),
        )

        mgr: PromptManager = getattr(self.bot, "prompt_manager", None)
        if not mgr:
            logger.info("No PromptManager attached to bot when /show_prompt called")
            await interaction.response.send_message("No active bot prompt loaded.")
            return

        logger.debug(
            "PromptManager state: prompt_present=%s updated_at=%s",
            bool(mgr.prompt),
            mgr.updated_at,
        )

        # If we don't have a prompt loaded, try fetching it now and log the outcome
        if not mgr.prompt:
            logger.info("No prompt loaded; attempting to fetch from API now")
            try:
                fetched = await mgr.fetch_prompt()
                logger.info("fetch_prompt result: %s", fetched)
            except Exception as e:
                logger.warning("Error while fetching prompt on-demand: %s", e)

        # truncate if too long
        prompt_text = mgr.prompt
        if len(prompt_text) > 1900:
            prompt_text = prompt_text[:1900] + "..."

        updated = mgr.updated_at or "unknown"
        await interaction.response.send_message(
            f"Current bot prompt (updated: {updated}):\n```\n{prompt_text}\n```"
        )
        logger.info(
            "Replied to /show_prompt (updated: %s) for user %s",
            updated,
            interaction.user,
        )

    @tasks.loop(minutes=5)
    async def refresh_prompt(self):
        await self.bot.wait_until_ready()
        await self.manager.fetch_prompt()

    @refresh_prompt.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()
        # initial fetch immediately
        await self.manager.fetch_prompt()


async def setup(bot: commands.Bot):
    await bot.add_cog(PromptLoader(bot))
    await bot.add_cog(PromptLoader(bot))
