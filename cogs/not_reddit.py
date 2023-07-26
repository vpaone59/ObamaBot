"""
https://github.com/vpaone59
"""

from discord.ext import commands
import os
import datetime
import asyncpraw

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

class Not_Reddit(commands.Cog):
    """ 
    Reddit API thingy
    """
    def __init__(self, bot):
        self.bot = bot
        self.reddit = asyncpraw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            password=PASSWORD,
            username=USERNAME,
            user_agent=USER_AGENT,
        )
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self} ready')
    
    @commands.command(aliases=['red'])
    async def get_latest_post(self, ctx, subreddit):
        subreddit_param = str(subreddit)

        try:
            # Fetch the latest post from the specified subreddit
            subreddit = await self.reddit.subreddit(subreddit_param)
            
            async for post in subreddit.new(limit=1):
                submission_datetime = datetime.datetime.fromtimestamp(
                    post.created_utc)
                time_difference = datetime.datetime.utcnow() - submission_datetime

                # Calculate the hours and minutes
                hours_ago = int(time_difference.total_seconds() // 3600)
                minutes_ago = int(
                    (time_difference.total_seconds() % 3600) // 60)

                # Display the time difference based on the condition
                if hours_ago >= 1:
                    await ctx.send(f"```Latest post from r/{post.subreddit} {hours_ago} hours ago:\nUpvotes: {post.score}\nTitle: {post.title}\nOP: {post.author}\nURL:``` {post.url}")
                else:
                    await ctx.send(f"```Latest post from r/{post.subreddit} {minutes_ago} minutes ago:\nUpvotes: {post.score}\nTitle: {post.title}\nOP: {post.author}\nURL:```{post.url}")
        
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Not_Reddit(bot))
