"""
Genius API integrator Cog for ObamaBot https://github.com/vpaone59
"""

import os
import random
import discord
from discord import app_commands
from discord.ext import commands
import lyricsgenius
from logging_config import create_new_logger

logger = create_new_logger(__name__)
GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")


class Genius(commands.Cog):
    """
    Genius API integrations Class
    """

    def __init__(self, bot):
        self.bot = bot
        self.genius = lyricsgenius.Genius(GENIUS_API_KEY)
        # Remove section headers from lyrics
        self.genius.remove_section_headers = True
        # Skip songs that have "remix", "live", etc.
        self.genius.skip_non_songs = True

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @app_commands.command(
        name="bar",
        description="Get a random bar from a random song in the input artist's discography",
    )
    async def get_random_bar_from_artist(
        self, interaction: discord.Interaction, artist_name: str
    ):
        """
        Get a random bar from a random song in an input artist_name's discography
        """
        # Defer the response to avoid timeout
        await interaction.response.defer()
        try:
            # Search for artist, get top 5 songs
            artist = self.genius.search_artist(
                artist_name, max_songs=5, sort="popularity"
            )
            if not artist:
                await interaction.response.send_message(
                    f"No artist found with name: {artist_name}"
                )
                return

            # Choose 1 of 5 random songs
            song = random.choice(artist.songs)
            if not song.lyrics:
                await interaction.response.send_message(
                    f"No lyrics found for song: {song.title}"
                )
                return

            # Split lyrics into lines and filter out empty lines
            lyrics_lines = [line for line in song.lyrics.split("\n") if line.strip()]

            # Get a random line
            random_bar = random.choice(lyrics_lines)
            random_bar2 = random.choice(lyrics_lines)

            await interaction.followup.send(
                f"{random_bar}, {random_bar2}\n**({song.title})**"
            )

        except Exception as e:
            logger.error("Error getting lyrics: %s", e)
            await interaction.response.send_message(f"An error occurred: {e}")


async def setup(bot):
    await bot.add_cog(Genius(bot))
