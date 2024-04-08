from discord.ext import commands
import sqlite3
import os
from logging_config import setup_logging

logger = setup_logging(__name__)
DB_PATH = os.getenv("DB_PATH")


class Counter(commands.Cog):
    """
    keeps a running tally of certain things...
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        runs when Cog is loaded and ready to use
        """
        logger.info("Cog ready", __name__)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        On every message we are going to check if it matches an entry in the database
        and then we update the entry's tally by +1
        """
        cap_message = str(message.content)
        if cap_message in counter_names:
            try:
                conn, cursor = connect_db()
                cursor.execute(
                    f"UPDATE counters SET tally=tally + 1 WHERE name = '{cap_message}'"
                )
                conn.commit()
            except Exception as err:
                await message.channel.send("Something went wrong: {}".format(err))
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
                "SUCCESS! USER: %s FUNCTION: %s VALUE: %s",
                ctx.message.author,
                __name__,
                counter_name,
            )
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "FAILURE! USER: %s FUNCTION: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                __name__,
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
                "SUCCESS! USER: %s FUNCTION: %s VALUE: %s",
                ctx.message.author,
                __name__,
                counter_name,
            )
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "FAILURE! USER: %s FUNCTION: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                __name__,
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
                "SUCCESS! USER: %s FUNCTION: %s VALUE: %s",
                ctx.message.author,
                __name__,
                counter_name,
            )
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "FAILURE! USER: %s FUNCTION: %s VALUE: %s ERROR: %s",
                ctx.message.author,
                __name__,
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
        Command to get a list of the current counters from the database
        """
        response_string = "String - Tally\n"

        try:
            get_counters()
            for c in counters_from_db:
                c_name = c[0]
                c_tally = c[1]
                response_string += f"{c_name}\t-\t{str(c_tally)}\n"

            await ctx.send(f"```{response_string}```")
            logger.info("USER: %s", ctx.message.author)
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))

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
            logger.info("USER: %s", ctx.message.author)
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
            logger.error(
                "FAILURE! USER: %s FUNCTION: %s ERROR: %s",
                ctx.message.author,
                __name__,
                err,
            )
        finally:
            cursor.close()
            conn.close()


def get_counters():
    """
    Function to get and set the list of counters and their tally's into global variables
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
    Function that connects to the database and returns a connection object and cursor object.
    Requires DB_PATH environment variable to be set
    """

    try:
        conn = sqlite3.connect(DB_PATH)  # type: ignore
        cursor = conn.cursor()
        logger.info("Cursor created for sqlite DB file at: %s", DB_PATH)
    except Exception as err:
        logger.error("Failed to connect to sqlite DB file at: %s --- %s", DB_PATH, err)

    return conn, cursor


async def setup(bot):
    await bot.add_cog(Counter(bot))
