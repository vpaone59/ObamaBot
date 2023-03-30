"""
Counter Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# test - create connection object to the database
try:
    cxn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),
        database=os.getenv("TARGET"))
    my_cursor = cxn.cursor()
except mysql.connector.Error:
    print(f"Connection to the target failed")


class Counter(commands.Cog):
    """
    keeps a running tally of certain things...
    """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        print(f'{self} ready')

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.content) == "meow":
            my_cursor.execute(
                "UPDATE trackers SET tally=tally+1 WHERE tracker_name = \"meows\"")
            cxn.commit()

    @commands.command(aliases=['reset'], description='Resets the tally for a given *tracker*')
    @commands.has_permissions(administrator=True)
    async def reset_tally(self, ctx, tracker):
        """
        Resets tally counter to zero for a user input tracker_name
        """
        db_conn = connect_db()

        sql = "UPDATE trackers SET tally=0 WHERE tracker_name = %s"
        val = tracker
        try:
            db_conn.execute(sql, (val,))
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        db_conn.commit()
        await ctx.send(f"```success. {tracker} is now 0```")


def connect_db():
    """
    Function that connects to the database
    """
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),
        database=os.getenv("obama"))

    return mydb


async def setup(client):
    await client.add_cog(Counter(client))
