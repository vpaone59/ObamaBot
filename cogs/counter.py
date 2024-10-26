"""
Counter Cog for ObamaBot https://github.com/vpaone59
"""

from discord.ext import commands
import sqlite3
import os
from logging_config import create_new_logger
from pathlib import Path

logger = create_new_logger(__name__)
DATABASE_PATH = Path("./database/obamabot.db").resolve()


class Counter(commands.Cog):
    """
    Attaches to a SQLite DB file and reads inputs from a `counters` table
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Runs when the cog is loaded
        """
        logger.info("%s ready", self.__cog_name__)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        On every message we are going to check if it matches an entry in the database
        and then we update the entry's tally by +1
        """
        message_content = str(message.content)
        if message_content in counter_names:
            try:
                conn, cursor = connect_db()
                cursor.execute(
                    f"UPDATE counters SET tally=tally + 1 WHERE name = '{message_content}'"
                )
                conn.commit()
                cursor.execute(
                    f"SELECT name, tally FROM counters WHERE name = '{message_content}'"
                )
                logger.info(
                    "USER: %s updated VALUE: %s", message.author, message_content
                )
            except Exception as err:
                await message.channel.send("Something went wrong: {}".format(err))
                logger.error(
                    "USER: %s VALUE: %s ERROR: %s",
                    message.message.author,
                    err,
                )
            finally:
                cursor.close()
                conn.close()
        else:
            return

    @commands.command(
        aliases=["reset"], description="Resets the tally for a given *tracker*"
    )
    @commands.has_permissions(administrator=True)
    async def reset_tally(self, ctx, counter_name):
        """
        Resets tally to zero for a user input counter name
        """
        sql = "UPDATE counters SET tally=0 WHERE name = ?"
        val = (counter_name,)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} is now 0```")
            logger.info(
                "USER: %s reset VALUE: %s",
                ctx.message.author,
                counter_name,
            )
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "USER: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                counter_name,
                err,
            )
        finally:
            cursor.close()
            conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_counter(self, ctx, counter_name):
        """
        Create a counter entry in the Database to keep a tally of
        """
        sql = "INSERT INTO counters (name, tally) VALUES (?, ?)"
        val = (counter_name, 0)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} is now being counted!```")
            logger.info(
                "USER: created %s VALUE: %s",
                ctx.message.author,
                counter_name,
            )
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "USER: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                counter_name,
                err,
            )
        finally:
            cursor.close()
            conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete_counter(self, ctx, counter_name):
        """
        Delete a counter entry in the Database by its name
        """
        sql = "DELETE FROM counters WHERE name = ?"
        val = (counter_name,)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} has now been deleted!```")
            logger.info(
                "USER: %s deleted VALUE: %s",
                ctx.message.author,
                counter_name,
            )
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "USER: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                counter_name,
                err,
            )
        finally:
            cursor.close()
            conn.close()

    @commands.command(aliases=["list", "tally"])
    @commands.has_permissions(administrator=True)
    async def list_counters(self, ctx):
        """
        List all counters in the counters table
        """
        response_string = "String - Tally\n"

        try:
            get_counters()
            for c in counters_from_db:
                c_name = c[0]
                c_tally = c[1]
                response_string += f"{c_name}\t-\t{str(c_tally)}\n"

            await ctx.send(f"```{response_string}```")
            logger.info("USER: %s listed counters", ctx.message.author)
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "USER: %s ERROR: %s",
                ctx.message.author,
                err,
            )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_tables(self, ctx):
        """
        Lists all tables in the database
        """
        try:
            conn, cursor = connect_db()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            await ctx.send("Tables in the database: " + ", ".join(table_names))
            logger.info("USER: %s listed tables", ctx.message.author)
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "USER: %s ERROR: %s",
                ctx.message.author,
                err,
            )
        finally:
            cursor.close()
            conn.close()


def get_counters():
    """
    Put counters and tallys into globall variables
    """
    global counter_names
    global counters_from_db
    counter_names = []
    counters_from_db = []
    conn, cursor = connect_db()

    try:
        cursor.execute("SELECT name, tally FROM counters")
        rows = cursor.fetchall()

        for row in rows:
            counter_names.append(row[0])
            counters_from_db.append([row[0], row[1]])
    except Exception as err:
        print("Something went wrong: {}".format(err))
    finally:
        cursor.close()
        conn.close()


def connect_db():
    """
    Connect to the database and return a connection and cursor object.
    Requires HOST_DB_PATH environment variable to be set
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)  # type: ignore
        cursor = conn.cursor()
        logger.info("Cursor created for sqlite DB file at: %s", DATABASE_PATH)
    except Exception as err:
        logger.error(
            "Failed to connect to sqlite DB file at: %s --- %s",
            DATABASE_PATH,
            err,
        )

    return conn, cursor


async def setup(bot):
    await bot.add_cog(Counter(bot))
