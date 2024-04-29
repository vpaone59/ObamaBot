"""
https://github.com/vpaone59
"""

import logging
from datetime import datetime, timezone, timedelta
import requests
from discord.ext import commands

logger = logging.getLogger(__name__)


class PredecessorStats(commands.Cog):
    """
    Cog that connects with the Omeda.city Predecessor API to return game and player information
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs once the Cog successfully loads
        """
        logger.info("%s ready", self)

    @commands.command()
    async def stats(self, ctx, *player_name):
        """
        Sends general information about the Predecessor player to the channel
        """
        player_name = " ".join(player_name)
        player_info = await get_player(await get_player_id(player_name))

        response_message = f"""```
Player ID: {player_info['id']}
Display Name: {player_info['display_name']}
Region: {player_info['region']}
Leaderboard: #{player_info['rank_active']}
Rank: {player_info['rank_title']}
MMR: {player_info['mmr']}```"""

        await ctx.channel.send(response_message)

    @commands.command(aliases=["lg", "last"])
    async def last(self, ctx, *player_name):
        """
        Sends the match history of a Predecessor player to the channel
        """
        player_name = " ".join(player_name)
        player_id = await get_player_id(player_name)

        if player_id:
            player_match_history = await get_player_match_history(player_id)

            start_time = (
                datetime.strptime(
                    player_match_history["start_time"], "%B %d, %Y %I:%M:%S %p"
                )
                .replace(tzinfo=timezone.utc)
                .astimezone(timezone(timedelta(hours=-5)))
            )

            # Convert end_time to EST
            end_time = (
                datetime.strptime(
                    player_match_history["end_time"], "%B %d, %Y %I:%M:%S %p"
                )
                .replace(tzinfo=timezone.utc)
                .astimezone(timezone(timedelta(hours=-5)))
            )

            response_message = f"""```
Player ID: {player_match_history['id']}
Game Time: {start_time.strftime("%B %d, %Y")} {start_time.strftime("%I:%M:%S %p")} - {end_time.strftime("%I:%M:%S %p")}
Name: {player_match_history['display_name']}
MMR: {player_match_history['mmr']}
MMR Change: {player_match_history['mmr_change']}
Minions Killed: {player_match_history['minions_killed']}
Level: {player_match_history['level']}
Kills: {player_match_history['kills']}
Deaths: {player_match_history['deaths']}
Assists: {player_match_history['assists']}
Total Damage Dealt to Heroes: {player_match_history['total_damage_dealt_to_heroes']}
Total Damage Taken from Heroes: {player_match_history['total_damage_taken_from_heroes']}
Gold Earned: {player_match_history['gold_earned']}```"""
            await ctx.channel.send(response_message)
        else:
            await ctx.channel.send(f"Player '{player_name}' not found.")

    @commands.command()
    async def hero_stats(self, ctx, *player_name):
        """
        Displays hero statistics for a player.
        """
        player_id = await get_player_id(player_name)

        if player_id:
            player_hero_stats = await get_player_hero_stats(player_id)

            if player_hero_stats:
                hero_stats = player_hero_stats.get("hero_statistics", [])
                # Initialize an empty string to store the formatted hero stats message
                formatted_stats = ""

                for hero in hero_stats:
                    # Extract hero stats
                    hero_name = hero["display_name"]
                    win_rate = hero["winrate"]
                    kda = hero["avg_kdar"]
                    total_kills = hero["kills"]
                    total_deaths = hero["deaths"]
                    total_assists = hero["assists"]

                    # Format hero stats
                    formatted_stats += f"**{hero_name}**\n"
                    formatted_stats += f"Winrate: {win_rate}\n"
                    formatted_stats += f"KDA: {kda}\n"
                    formatted_stats += f"Total Kills: {total_kills}\n"
                    formatted_stats += f"Total Deaths: {total_deaths}\n"
                    formatted_stats += f"Total Assists: {total_assists}\n\n"

                    # Send the formatted hero stats to the channel
                await ctx.send(formatted_stats)

            else:
                await ctx.send("No hero statistics found for the player.")
        else:
            await ctx.send(f"Player '{player_name}' not found.")


async def get_player(player_id):
    """
    Fetches general information about the player from omeda.city API.
    """
    url = f"https://omeda.city/players/{player_id}.json"
    try:
        response = requests.get(url, timeout=15)
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
        response = requests.get(url, params=params, timeout=15)
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
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an error for bad status codes
        matches_data = response.json()["matches"]
        player_info = None
        for match in matches_data:
            for player in match["players"]:
                if player["id"] == player_id:
                    player_info = player
                    player_info["start_time"] = format_date(match["start_time"])
                    player_info["end_time"] = format_date(match["end_time"])
                    break
            if player_info:
                break
        return player_info
    except requests.RequestException as e:
        logger.error("Error fetching data: %s : Player Id - %s", e, player_id)
        return None


async def get_player_hero_stats(player_id):
    """
    Fetches hero stats for the player ID from the Omeda.city API.
    """
    url = f"https://omeda.city/players/{player_id}/hero_statistics.json"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Raise an error for bad status codes
        player_hero_data = response.json()
        if player_hero_data:
            return player_hero_data
        logger.info("Player '%s' not found.", player_id)
        return None
    except requests.RequestException as e:
        logger.error("Error fetching data: %s", e)
        return None


def format_date(date_string):
    """
    Formats the date string into a readable format.
    """
    date_object = datetime.fromisoformat(date_string[:-1])
    return date_object.strftime("%B %d, %Y %I:%M:%S %p")


async def setup(bot):
    """ """
    await bot.add_cog(PredecessorStats(bot))
