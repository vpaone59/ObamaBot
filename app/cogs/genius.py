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
        Returns random lyric bars from a random song by the specified artist.

        Args:
            artist_name: The name of the artist to search for
        """
        logger.info(
            "User %s requested lyrics for artist: %s", interaction.user, artist_name
        )

        # Weighted random selection - prefer popularity sorting
        sort_type = ["popularity"] * 8 + ["title"] * 2
        sort_type_choice = random.choice(sort_type)

        await interaction.response.defer()

        try:
            # Validate API key
            if not GENIUS_API_KEY:
                logger.error("GENIUS_API_KEY not configured")
                await interaction.followup.send(
                    "Genius API is not configured. Please contact an administrator."
                )
                return

            logger.info(
                "Searching for artist '%s' using %s sort", artist_name, sort_type_choice
            )

            # Search for artist
            artist = self.genius.search_artist(
                artist_name,
                max_songs=5,
                sort=sort_type_choice,
                per_page=5,
                get_full_info=False,
            )

            if not artist:
                logger.warning("No artist found for: %s", artist_name)
                await interaction.followup.send(
                    f"No artist found with name: **{artist_name}**\nTry checking the spelling or using a different name."
                )
                return

            if not artist.songs:
                logger.warning("No songs found for artist: %s", artist_name)
                await interaction.followup.send(
                    f"No songs found for **{artist.name}**\nThis artist might not have lyrics available."
                )
                return

            # Choose random song from available songs
            song = random.choice(artist.songs)
            logger.info("Selected song: %s by %s", song.title, song.artist)

            if not song.lyrics:
                logger.warning("No lyrics found for song: %s", song.title)
                await interaction.followup.send(
                    f"No lyrics found for **{song.title}** by {song.artist}\nTry using the command again for a different song."
                )
                return

            # Process lyrics
            lyrics_lines = [
                line.strip()
                for line in song.lyrics.split("\n")
                if line.strip()
                and not line.strip().startswith("[")
                and len(line.strip()) > 10
            ]

            if len(lyrics_lines) < 2:
                logger.warning("Insufficient lyrics for song: %s", song.title)
                await interaction.followup.send(
                    f"Not enough lyric content found for **{song.title}**\nTry using the command again for a different song."
                )
                return

            # Get random bars
            random_bar1 = random.choice(lyrics_lines)
            random_bar2 = random.choice(lyrics_lines)

            # Ensure we don't get the same line twice if possible
            if len(lyrics_lines) > 1 and random_bar1 == random_bar2:
                available_lines = [line for line in lyrics_lines if line != random_bar1]
                if available_lines:
                    random_bar2 = random.choice(available_lines)

            logger.info(
                "Successfully retrieved lyrics for %s - %s", song.artist, song.title
            )

            embed = discord.Embed(
                title="🎤 Random Bars",
                description=f"*{random_bar1}*\n\n*{random_bar2}*",
                color=0x1DB954,  # Spotify green
            )
            embed.set_footer(text=f"{song.artist} - {song.title}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(
                "Error getting lyrics for %s: %s", artist_name, e, exc_info=True
            )
            await interaction.followup.send(
                f"An error occurred while searching for lyrics.\nPlease try again or contact an administrator if the issue persists."
            )


async def setup(bot):
    await bot.add_cog(Genius(bot))
