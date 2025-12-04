"""
Obama AI Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This cog allows users to interact with an AI that generates responses in the style of Barack Obama.
"""

import asyncio
import json
import os

import requests
from discord import Interaction, app_commands
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)

AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")


class AIChat(commands.Cog):
    """
    A cog that allows users to interact with an AI that generates responses in the style of Barack Obama.
    This cog uses the Ollama API to generate responses based on user prompts.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Validate environment variables
        if not AI_SYSTEM_PROMPT:
            logger.error("AI_SYSTEM_PROMPT environment variable not set.")
        if not OLLAMA_API_URL:
            logger.error("OLLAMA_API_URL environment variable not set.")
        if not OLLAMA_MODEL:
            logger.warning("OLLAMA_MODEL not set. Using default model: gemma3:1b")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @app_commands.command(name="askobama", description="Ask ObamaBot a question")
    async def ai_chat_slash_command(self, interaction: Interaction, query: str):
        """
        Generate a response to the user's input prompt when they run this command.
        """
        logger.info("Slash command 'askobama' invoked with query: %s", query)
        try:
            response_text = await asyncio.get_event_loop().run_in_executor(
                None, self.generate_ai_response, query
            )

            if not response_text:
                response_text = (
                    "I'm sorry, but I couldn't generate a response at this time."
                )

            await interaction.response.send_message(response_text)

        except Exception as e:
            logger.error("Error in ai_chat_slash_command: %s", e)
            await interaction.response.send_message(
                "I'm sorry, but I couldn't generate a response at this time."
            )

    @commands.command(aliases=["obama", "askobama"])
    async def chat(self, ctx: commands.Context, *, query: str = None):
        """
        Prefix activated AI chat command. Does the same thing as ai_chat_slash_command
        """
        logger.info("Prefix command 'chat' invoked with query: %s", query)
        try:
            if not query:
                await ctx.send(
                    "Please provide a question after the command. Example: `!obama What do you think about climate change?`"
                )
                return

            # Defer typing to show the bot is working
            async with ctx.typing():
                response_text = await asyncio.get_event_loop().run_in_executor(
                    None, self.generate_ai_response, query
                )

            if not response_text:
                response_text = (
                    "I'm sorry, but I couldn't generate a response at this time."
                )

            await ctx.send(response_text)

        except Exception as e:
            logger.error("Error in chat command: %s", e)
            await ctx.send(
                "I'm sorry, but I couldn't generate a response at this time."
            )

    def generate_ai_response(self, prompt: str) -> str:
        """
        Generate a response from the Ollama API and return the complete text.
        This runs in a separate thread via run_in_executor.
        """
        logger.info("Generating AI response for prompt: %s", prompt)
        response_text = ""

        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": AI_SYSTEM_PROMPT,
                },
                stream=True,
                timeout=30,  # Increased timeout
            )

            logger.info("API request sent. Status code: %d", response.status_code)

            # Check if the request was successful
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            response_text += chunk["response"]
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON from line: %s", line)

            if not response_text:
                logger.warning("No response text generated from the API.")

        except requests.exceptions.RequestException as e:
            logger.error("Request error: %s", e)
        except Exception as e:
            logger.error("Unexpected error in generate_ai_response: %s", e)

        return response_text


async def setup(bot: commands.Bot):
    # Check if required environment variables are set
    if not AI_SYSTEM_PROMPT:
        logger.error(
            "AI_SYSTEM_PROMPT environment variable not set. ObamaAI cog not loaded."
        )
        return

    if not OLLAMA_API_URL:
        logger.error(
            "OLLAMA_API_URL environment variable not set. ObamaAI cog not loaded."
        )
        return

    await bot.add_cog(AIChat(bot))
