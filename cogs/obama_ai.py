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

OBAMA_SYSTEM_PROMPT = os.getenv("OBAMA_SYSTEM_PROMPT")
OBAMA_AI_API_URL = os.getenv("OBAMA_AI_API_URL")
logger = create_new_logger(__name__)


class ObamaAI(commands.Cog):
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

    @commands.command(name="askobama")
    async def obama_ai(self, ctx, *, prompt: str):
        """
        Generate a response in the style of Barack Obama.
        """
        try:
            # await ctx.response.defer(thinking=True)
            response_text = await asyncio.get_event_loop().run_in_executor(
                None, self.generate_obama_response, prompt
            )

            # Send the complete response
            await ctx.send(response_text)

        except Exception as e:
            logger.error("Error in obama_ai command: %s", e)
            await ctx.send(
                "I'm sorry, but I couldn't generate a response at this time."
            )

    def generate_obama_response(self, prompt):
        """
        Generate a response from the Ollama API and return the complete text.
        This runs in a separate thread via run_in_executor.
        """
        response_text = ""

        response = requests.post(
            OBAMA_AI_API_URL,
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "system": OBAMA_SYSTEM_PROMPT,
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
    if not OBAMA_SYSTEM_PROMPT:
        logger.error(
            "OBAMA_SYSTEM_PROMPT environment variable not set. ObamaAI cog not loaded."
        )
        return

    if not OBAMA_AI_API_URL:
        logger.error(
            "OBAMA_AI_API_URL environment variable not set. ObamaAI cog not loaded."
        )
        return

    await bot.add_cog(ObamaAI(bot))
