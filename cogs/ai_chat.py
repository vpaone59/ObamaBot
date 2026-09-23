"""
Obama AI Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This cog allows users to interact with an AI that generates responses in the style of Barack Obama.
"""

import asyncio
import os
import time

import ollama
from discord import Interaction, app_commands
from discord.ext import commands

from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# Fallback system prompt if none provided by prompt loader
FALLBACK_SYSTEM_PROMPT = (
    "You are Barack Obama, the 44th President of the United States."
)
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")


class AIChat(commands.Cog):
    """
    A cog that allows users to interact with an AI that generates responses in the style of Barack Obama.
    This cog uses the Ollama API to generate responses based on user prompts.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = ollama.Client(host=OLLAMA_API_URL)
        self.api_available = False

        # system prompt will be read dynamically from bot.prompt_manager when generating
        self.system_prompt = None

        logger.info(
            "AIChat initialized | Ollama URL: %s | Model: %s",
            OLLAMA_API_URL,
            OLLAMA_MODEL,
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded. Checks Ollama API health.
        """
        logger.info("%s ready", self.__cog_name__)
        await self._check_ollama_health()

    async def _check_ollama_health(self):
        """
        Check if Ollama API is reachable and model is available.
        Runs asynchronously without blocking bot startup.
        """
        try:
            models = await asyncio.get_event_loop().run_in_executor(
                None, self.client.list
            )
            available_models = [m.get("name", "") for m in models.get("models", [])]

            if OLLAMA_MODEL in available_models:
                logger.info(
                    "Ollama API health check passed | Available models: %s",
                    ", ".join(available_models),
                )
                self.api_available = True
            else:
                logger.warning(
                    "Model %s not available | Available: %s",
                    OLLAMA_MODEL,
                    ", ".join(available_models),
                )
                self.api_available = False
        except Exception as e:
            logger.error(
                "Ollama API health check failed | URL: %s | Error: %s",
                OLLAMA_API_URL,
                e,
            )
            self.api_available = False

    @app_commands.command(name="askobama", description="Ask ObamaBot a question")
    async def ai_chat_slash_command(self, interaction: Interaction, query: str):
        """
        Generate a response to the user's input prompt when they run this command.
        """
        logger.info("Slash command 'askobama' invoked | Query: %s", query[:100])
        await interaction.response.defer()

        try:
            response_text = await asyncio.get_event_loop().run_in_executor(
                None, self.generate_ai_response, query
            )

            if not response_text or response_text.isspace():
                logger.warning(
                    "Empty response from AI | Query: %s | API available: %s",
                    query[:100],
                    self.api_available,
                )
                response_text = (
                    "I'm unable to generate a response right now. Please try again."
                )

            await interaction.followup.send(response_text)
            logger.info(
                "Response sent successfully | Length: %d chars", len(response_text)
            )

        except Exception as e:
            logger.error(
                "Error in ai_chat_slash_command: %s | Query: %s",
                e,
                query[:100],
            )
            await interaction.followup.send(
                "An error occurred while processing your request."
            )

    @commands.command(aliases=["obama", "askobama"])
    async def chat(self, ctx: commands.Context, *, query: str = None):
        """
        Prefix activated AI chat command. Does the same thing as ai_chat_slash_command
        """
        logger.info(
            "Prefix command 'chat' invoked | Query: %s",
            query[:100] if query else "None",
        )

        try:
            if not query or query.isspace():
                await ctx.send(
                    "Please provide a question after the command. Example: `!obama What do you think about climate change?`"
                )
                logger.warning("Chat command invoked without query")
                return

            # Defer typing to show the bot is working
            async with ctx.typing():
                response_text = await asyncio.get_event_loop().run_in_executor(
                    None, self.generate_ai_response, query
                )

            if not response_text or response_text.isspace():
                logger.warning(
                    "Empty response from AI | Query: %s | API available: %s",
                    query[:100],
                    self.api_available,
                )
                response_text = (
                    "I'm unable to generate a response right now. Please try again."
                )

            await ctx.send(response_text)
            logger.info(
                "Response sent successfully | Length: %d chars", len(response_text)
            )

        except Exception as e:
            logger.error(
                "Error in chat command: %s | Query: %s",
                e,
                query[:100] if query else "None",
            )
            await ctx.send("An error occurred while processing your request.")

    def generate_ai_response(self, prompt: str) -> str:
        """
        Generate a response from the Ollama API using the official Python library.
        This runs in a separate thread via run_in_executor.

        Returns: Generated response text, or empty string on failure
        """
        logger.info(
            "Generating AI response | Model: %s | Prompt: %s",
            OLLAMA_MODEL,
            prompt[:100],
        )
        response_text = ""
        start_time = time.time()

        try:
            # Call Ollama API
            # Prefer prompt from PromptManager if available
            mgr = getattr(self.bot, "prompt_manager", None)
            system_prompt = None
            if mgr and mgr.prompt:
                system_prompt = mgr.prompt
            else:
                system_prompt = FALLBACK_SYSTEM_PROMPT

            response = self.client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                system=system_prompt,
                stream=False,
            )

            response_text = response.get("response", "").strip()
            elapsed_time = time.time() - start_time

            if response_text:
                logger.info(
                    "AI response generated | Length: %d chars | Time: %.2fs",
                    len(response_text),
                    elapsed_time,
                )
            else:
                logger.warning(
                    "Empty response from Ollama | Model: %s | Time: %.2fs",
                    OLLAMA_MODEL,
                    elapsed_time,
                )

        except ollama.ResponseError as e:
            logger.error(
                "Ollama API response error | Status: %s | Error: %s",
                getattr(e, "status_code", "unknown"),
                e.error if hasattr(e, "error") else str(e),
            )
        except ollama.RequestError as e:
            logger.error("Ollama API request error | Error: %s", e)
        except Exception as e:
            logger.error(
                "Unexpected error in generate_ai_response | Type: %s | Error: %s",
                type(e).__name__,
                e,
            )

        return response_text


async def setup(bot: commands.Bot):
    """Setup function for the AIChat cog"""
    await bot.add_cog(AIChat(bot))
