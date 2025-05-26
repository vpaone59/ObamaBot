"""
General Commands Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

These are general use commands that any bot should have by default.
"""

import os
import json
import asyncio
import requests
from discord.ext import commands
from logging_config import create_new_logger

OBAMA_SYSTEM_PROMPT = """
You are Barack Obama, the 44th President of the United States. Respond in your distinct speaking style, 
using phrases like "Let me be clear" and "folks." Maintain a thoughtful, measured tone while being. 
Avoid policy specifics from after your presidency ended in January 2017.
Ensure each response is less than 2000 characters, and if the response exceeds this limit, 
truncate it to fit within the limit while preserving the essence of the message.
"""
OBAMA_AI_API_URL = os.getenv("OBAMA_AI_API_URL")
logger = create_new_logger(__name__)


class ObamaAI(commands.Cog):
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
        print(f"Received prompt: {prompt}")
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
    await bot.add_cog(ObamaAI(bot))
