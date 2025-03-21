"""
https://github.com/vpaone59
"""

import os
import base64
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from logging_config import create_new_logger

logger = create_new_logger(__name__)

CLIEND_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


class Spotify(commands.Cog):
    """
    Spotify API Cog for ObamaBot
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        pass

    @commands.command()
    async def test_spot(self, ctx):
        """"""
        print("running")
        await get_spotify_token(CLIEND_ID, CLIENT_SECRET)


async def get_spotify_token(client_id: str, client_secret: str):
    """
    Returns a Spotify auth token using the client ID and client secret.
    """
    token_url = "https://accounts.spotify.com/api/token"
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, headers=headers, data=data) as response:
            # TODO: need to close the session at some point
            response_json = await response.json()
            logger.info(
                "Generated new Spotify auth token from: %s Access token: %s",
                token_url,
                response_json["access_token"],
            )


async def setup(bot):
    await bot.add_cog(Spotify(bot))
