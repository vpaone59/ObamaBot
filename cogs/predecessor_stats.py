"""
https://github.com/vpaone59
"""

import requests
from discord.ext import commands
import logging


logger = logging.getLogger(__name__)


class PredecessorStats(commands.Cog):
    """
    Class that connects with tha Predecessor Omeda.city API to return game information
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """ """
        logger.info("%s ready", self)

    @commands.command(aliases=["pred"])
    async def get_player(self, ctx, *player_name):
        """
        Sends general information about the Predecessor player to the channel
        """
        player_name = " ".join(player_name)
        player_info = await get_player_general(await get_player_id(player_name))

        response_message = f"Player ID: {player_info['id']}\n\
            Display Name: {player_info['display_name']}\n\
            Region: {player_info['region']}\n\
            Rank: {player_info['rank']}\n\
            Active Rank: {player_info['rank_active']}\n\
            Rank Title: {player_info['rank_title']}\n\
            Rank Image: (https://omeda.city{player_info['rank_image']})\n\
            Ranked: {player_info['is_ranked']}\n\
            MMR: {player_info['mmr']}"

        await ctx.channel.send(response_message)


async def get_player_general(player_id):
    """
    Fetches general information about the player from omeda.city API.
    """
    url = f"https://omeda.city/players/{player_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.RequestException as e:
        logger.error("Error fetching data: %s", e)
        return None


async def get_player_id(player_name):
    """
    Fetches the player ID from the Omeda.city API based on the player's name.
    """
    url = "https://omeda.city/players.json"
    params = {"filter[name]": player_name}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        players_data = response.json()
        if players_data:
            # Assuming the API returns a list of players, we'll take the first one
            return players_data[0]["id"]
        logger.info("Player '%s' not found.", player_name)
        return None
    except requests.RequestException as e:
        logger.error("Error fetching data: %s", e)
        return None


async def setup(bot):
    """ """
    await bot.add_cog(PredecessorStats(bot))
