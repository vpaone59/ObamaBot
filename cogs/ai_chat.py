"""
Obama AI Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This cog allows users to interact with an AI that generates responses in the style of Barack Obama.
Includes conversation memory and user customization support.
"""

import asyncio
import os
import time
from pathlib import Path

import discord
import ollama
from discord import Interaction, app_commands
from discord.ext import commands

from utils.conversation_manager import ConversationManager
from utils.logging_config import create_new_logger

logger = create_new_logger(__name__)

# Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
PAUL_DISCORD_ID = os.getenv("PAUL_DISCORD_ID")

# Load system prompt from file or fallback
SYSTEM_PROMPT_FILE = Path("./system_prompt.txt")
FALLBACK_SYSTEM_PROMPT = (
    "You are Barack Obama, the 44th President of the United States."
)


def load_system_prompt() -> str:
    """Load system prompt from file or return fallback."""
    if SYSTEM_PROMPT_FILE.exists():
        try:
            prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
            logger.info("Loaded system prompt from %s", SYSTEM_PROMPT_FILE)
            return prompt
        except (OSError, UnicodeDecodeError):
            logger.warning("Failed to load system prompt file")
            return FALLBACK_SYSTEM_PROMPT
    else:
        logger.debug("System prompt file not found, using fallback")
        return FALLBACK_SYSTEM_PROMPT


def generate_special_user_rules() -> str:
    """Generate special user rules (e.g., for Paul)."""
    rules = []

    if PAUL_DISCORD_ID:
        try:
            paul_id = int(PAUL_DISCORD_ID)
            rules.append(
                f"- If the message author's ID is {paul_id} (Paul), refer to him as **Daddy Paul** in your response."
            )
        except ValueError:
            logger.warning("Invalid PAUL_DISCORD_ID format: %s", PAUL_DISCORD_ID)

    return "\n".join(rules) if rules else "No special user rules configured."


class AIChat(commands.Cog):
    """
    A cog that allows users to interact with an AI that generates responses in the style of Barack Obama.
    This cog uses the Ollama API to generate responses based on user prompts.
    Includes conversation memory for context and user customization support.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = ollama.Client(host=OLLAMA_API_URL)
        self.api_available = False
        self.system_prompt = load_system_prompt()
        self.special_user_rules = generate_special_user_rules()

        logger.info(
            "AIChat initialized | Ollama URL: %s | Model: %s | Special rules configured: %s",
            OLLAMA_API_URL,
            OLLAMA_MODEL,
            "yes" if PAUL_DISCORD_ID else "no",
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
        except (ollama.RequestError, ollama.ResponseError):
            logger.error(
                "Ollama API health check failed | URL: %s",
                OLLAMA_API_URL,
            )
            self.api_available = False

    @app_commands.command(name="askobama", description="Ask ObamaBot a question")
    async def ai_chat_slash_command(self, interaction: Interaction, query: str):
        """
        Generate a response to the user's input prompt when they run this command.
        Includes conversation history for context.
        """
        logger.info(
            "Slash command 'askobama' invoked by %s | Query: %s",
            interaction.user,
            query[:100],
        )
        await interaction.response.defer()

        try:
            # Get or create user record
            user = ConversationManager.get_or_create_user(
                interaction.user.id, interaction.user.name
            )
            logger.debug(
                "User record | ID: %s | Name: %s",
                user["discord_id"],
                user["display_name"],
            )

            # Get conversation history
            history = ConversationManager.get_conversation_history(interaction.user.id)

            # Generate response with conversation context
            response_text = await asyncio.get_event_loop().run_in_executor(
                None,
                self.generate_ai_response,
                query,
                interaction.user.id,
                interaction.user.name,
                user,
                history,
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

            # Store the exchange in conversation history
            ConversationManager.add_message_to_history(
                interaction.user.id, "user", query
            )
            ConversationManager.add_message_to_history(
                interaction.user.id, "assistant", response_text
            )

            await interaction.followup.send(response_text)
            logger.info(
                "Response sent successfully | User: %s | Length: %d chars",
                interaction.user,
                len(response_text),
            )

        except discord.DiscordException:
            logger.exception(
                "Discord error in ai_chat_slash_command for user %s", interaction.user
            )
            await interaction.followup.send(
                "An error occurred while processing your request."
            )

    @commands.command(aliases=["obama", "askobama"])
    async def chat(self, ctx: commands.Context, *, query: str | None = None):
        """
        Prefix activated AI chat command. Includes conversation history for context.
        """
        logger.info(
            "Prefix command 'chat' invoked by %s | Query: %s",
            ctx.author,
            query[:100] if query else "None",
        )

        try:
            if not query or query.isspace():
                await ctx.send(
                    "Please provide a question after the command. Example: `!obama What do you think about climate change?`"
                )
                logger.warning("Chat command invoked without query by %s", ctx.author)
                return

            # Get or create user record
            user = ConversationManager.get_or_create_user(
                ctx.author.id, ctx.author.name
            )
            logger.debug(
                "User record | ID: %s | Name: %s",
                user["discord_id"],
                user["display_name"],
            )

            # Get conversation history
            history = ConversationManager.get_conversation_history(ctx.author.id)

            # Defer typing to show the bot is working
            async with ctx.typing():
                response_text = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.generate_ai_response,
                    query,
                    ctx.author.id,
                    ctx.author.name,
                    user,
                    history,
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

            # Store the exchange in conversation history
            ConversationManager.add_message_to_history(ctx.author.id, "user", query)
            ConversationManager.add_message_to_history(
                ctx.author.id, "assistant", response_text
            )

            await ctx.send(response_text)
            logger.info(
                "Response sent successfully | User: %s | Length: %d chars",
                ctx.author,
                len(response_text),
            )

        except discord.DiscordException:
            logger.exception("Discord error in chat command for user %s", ctx.author)
            await ctx.send("An error occurred while processing your request.")

    def generate_ai_response(
        self,
        prompt: str,
        discord_id: int,
        user_name: str,
        user: dict,
        conversation_history: list,
    ) -> str:
        """
        Generate a response from the Ollama API using conversation context and user data.
        This runs in a separate thread via run_in_executor.

        Args:
            prompt: User's current message
            discord_id: User's Discord ID
            user_name: User's Discord display name
            user: User record from database
            conversation_history: List of previous messages in conversation

        Returns:
            Generated response text, or empty string on failure
        """
        logger.info(
            "Generating AI response | User: %s | Discord ID: %s | Model: %s",
            user_name,
            discord_id,
            OLLAMA_MODEL,
        )
        response_text = ""
        start_time = time.time()

        try:
            # Build system prompt with special user rules and conversation context
            system_prompt = self.system_prompt.replace(
                "{SPECIAL_USER_RULES}", self.special_user_rules
            )

            # Add conversation context if available
            if conversation_history:
                history_context = ConversationManager.format_history_for_context(
                    conversation_history, user_name
                )
                system_prompt = f"{system_prompt}\n\n{history_context}"

            # Add current user info
            system_prompt += (
                f"\n\n## Current Request\n**User**: {user_name} (ID: {discord_id})"
            )

            logger.debug(
                "System prompt size: %d chars | History messages: %d",
                len(system_prompt),
                len(conversation_history),
            )

            # Call Ollama API with context
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
                    "AI response generated | User: %s | Length: %d chars | Time: %.2fs",
                    user_name,
                    len(response_text),
                    elapsed_time,
                )
            else:
                logger.warning(
                    "Empty response from Ollama | User: %s | Model: %s | Time: %.2fs",
                    user_name,
                    OLLAMA_MODEL,
                    elapsed_time,
                )

        except ollama.ResponseError as e:
            logger.error(
                "Ollama API response error | User: %s | Status: %s | Error: %s",
                user_name,
                getattr(e, "status_code", "unknown"),
                e.error if hasattr(e, "error") else str(e),
            )
        except ollama.RequestError:
            logger.error("Ollama API request error | User: %s", user_name)
        except (OSError, TimeoutError, ValueError) as e:
            logger.error(
                "Error in generate_ai_response | User: %s | Type: %s",
                user_name,
                type(e).__name__,
            )

        return response_text


async def setup(bot: commands.Bot):
    """Setup function for the AIChat cog"""
    await bot.add_cog(AIChat(bot))
