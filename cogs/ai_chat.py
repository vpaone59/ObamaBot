"""
Obama AI Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This cog allows users to interact with an AI that generates responses in the style of Barack Obama.
"""

import os
import json
import asyncio
import requests
from discord.ext import commands
from logging_config import create_new_logger

AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
logger = create_new_logger(__name__)


class AIChat(commands.Cog):
    """
    A cog that allows users to interact with an AI that generates responses in the style of Barack Obama.
    This cog uses the Ollama API to generate responses based on user prompts.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.command(aliases=["askobama", "obama"])
    async def ai_chat(self, ctx, *, prompt: str):
        """
        Generate a response to the user's input prompt when they run this command.
        """
        try:
            # await ctx.response.defer(thinking=True)
            response_text = await asyncio.get_event_loop().run_in_executor(
                None, self.generate_ai_response, prompt
            )

            # Send the complete response
            await ctx.send(response_text)

        except Exception as e:
            logger.error("Error in ai_chat command: %s", e)
            await ctx.send(
                "I'm sorry, but I couldn't generate a response at this time."
            )

    def generate_ai_response(self, prompt):
        """
        Generate a response from the Ollama API and return the complete text.
        This runs in a separate thread via run_in_executor.
        """
        response_text = ""

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "system": AI_SYSTEM_PROMPT,
            },
            stream=True,
            timeout=10,
        )

        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        response_text += chunk["response"]
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from line: %s", line)

        return response_text


async def setup(bot):
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
