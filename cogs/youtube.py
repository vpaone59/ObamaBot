"""
https://github.com/vpaone59
"""

import os
from datetime import datetime
from discord.ext import commands
import logging
import googleapiclient.discovery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ratemytakeaway_channel_id = "UCd03Ksc7VNypelv_TM3SjSg"
logger = logging.getLogger(__name__)


class Youtube(commands.Cog):
    """
    YouTube API integrations Class
    """

    def __init__(self, bot):
        self.bot = bot

        # Configure the logger to save logs to bot.log
        if not logger.handlers:
            file_handler = logging.FileHandler("bot.log")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logger.addHandler(file_handler)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self} ready")

    @commands.command(aliases=["rmt", "danny"])
    async def get_latest_video(self, ctx, channel_id=ratemytakeaway_channel_id):
        """
        Get the most recent upload from any YouTube channel by their channel ID
        Default channel ID is set to Rate My Takeaway's channel ID
        """
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY")
        )

        # Setup for the first request to get the most recent video from the channel
        yt_video_request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="date",  # Order by date so we know it is the most recent
            maxResults=1,  # Fetch one result aka most recent video
        )

        try:
            video_response = yt_video_request.execute()
            if "items" in video_response:
                result = video_response["items"][0]
                video_snippet = result["snippet"]
                print(video_snippet)

                # Convert the publishedAt string to a datetime object
                publishedAt_str = video_snippet["publishedAt"]
                published_at = datetime.strptime(publishedAt_str, "%Y-%m-%dT%H:%M:%SZ")
                # Format it in a readable way
                formatted_publishedAt = published_at.strftime("%B %d, %Y %H:%M:%S")

                latest_video = {
                    "title": video_snippet["title"],
                    "description": video_snippet["description"],
                    "published_at": formatted_publishedAt,
                    "thumbnail": video_snippet["thumbnails"]["medium"]["url"],
                    "video_url": f"https://www.youtube.com/watch?v={result['id']['videoId']}",
                }

            await ctx.send(
                f"**{latest_video['title']}\n{latest_video['published_at']}**\n*{latest_video['description']}*\n{latest_video['video_url']}"
            )

        except Exception as e:
            logger.error(f"USER: {ctx.message.author} ERROR: {e}")
            await ctx.send(f"{e}")


async def setup(bot):
    await bot.add_cog(Youtube(bot))
