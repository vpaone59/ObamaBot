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
    async def pred_player_stats(self, ctx, *player_name):
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
            MMR: {player_info['mmr']}"

        await ctx.channel.send(response_message)

    @commands.command(aliases=["predmh"])
    async def pred_player_matches(self, ctx, *player_name):
        """
        Sends the match history of a Predecessor player to the channel
        """
        player_name = " ".join(player_name)
        player_id = await get_player_id(player_name)
        print(player_id, player_name)
        if player_id:
            player_match_history = await get_player_match_history(player_id)
            print(player_match_history)
            response_message = f"""
Start Time: {player_match_history['start_time']}
End Time: {player_match_history['end_time']}
Player ID: {player_match_history['id']}
Name: {player_match_history['display_name']}
MMR: {player_match_history['mmr']}
MMR Change: {player_match_history['mmr_change']}
Minions Killed: {player_match_history['minions_killed']}
Kills: {player_match_history['kills']}
Deaths: {player_match_history['deaths']}
Assists: {player_match_history['assists']}
Total Damage Dealt to Heroes: {player_match_history['total_damage_dealt_to_heroes']}
Total Damage Taken from Heroes: {player_match_history['total_damage_taken_from_heroes']}
Gold Earned: {player_match_history['gold_earned']}
                                """
            await ctx.channel.send(response_message)
        else:
            await ctx.channel.send(f"Player '{player_name}' not found.")


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


async def get_player_match_history(player_id):
    """
    Fetches the match history of a player from omeda.city API.
    """
    url = f"https://omeda.city/players/{player_id}/matches.json"
    params = {"time_frame": "1D"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        matches_data = response.json()["matches"]
        player_info = None
        for match in matches_data:
            for player in match["players"]:
                if player["id"] == player_id:
                    player_info = player
                    player_info["start_time"] = match["start_time"]
                    player_info["end_time"] = match["end_time"]
                    break
            if player_info:
                break
        return player_info
    except requests.RequestException as e:
        logger.error("Error fetching data: %s", e)
        return None


async def setup(bot):
    """ """
    await bot.add_cog(PredecessorStats(bot))
