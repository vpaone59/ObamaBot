from discord.ext import commands
import sqlite3
import os

counter_names = []
counters_from_db = []


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
        print(f"{self} ready")
        # When this Cog first loads we grab a list of every entry in the DB name_of_counters column
        # and add it to global variable list counters_from_db
        get_counters()

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
                    f"UPDATE counters SET tally_counter=tally_counter + 1 WHERE name_of_counter = '{cap_message}'"
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
        Resets tally_counter to zero for a user input tracker_name
        """
        sql = "UPDATE counters SET tally_counter=0 WHERE name_of_counter = ?"
        val = (counter_name,)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} is now 0```")
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_counter(self, ctx, counter_name):
        """
        Create an entry in the Database to keep a tally of
        """
        sql = "INSERT INTO counters (name_of_counter, tally_counter) VALUES (?, ?)"
        val = (counter_name, 0)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} is now being counted!```")
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete_counter(self, ctx, counter_name):
        """
        Delete an entry in the Database
        """
        sql = "DELETE FROM counters WHERE name_of_counter = ?"
        val = (counter_name,)
        try:
            conn, cursor = connect_db()
            cursor.execute(sql, val)
            conn.commit()
            await ctx.send(f"```success. {counter_name} has now been deleted!```")
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            conn.close()

    @commands.command(aliases=["list_all"])
    @commands.has_permissions(administrator=True)
    async def list_counters(self, ctx):
        """
        Command to get a list of the current counters from the database
        """
        counter_string = "String - Tally\n"

        try:
            get_counters()
            for c in counters_from_db:
                c_name = c[0]
                c_tally = c[1]
                counter_string += f"{c_name}\t-\t{str(c_tally)}\n"

            await ctx.send(f"```{counter_string}```")
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))


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
        cursor.execute("SELECT name_of_counter, tally_counter FROM counters")
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
    Function that connects to the database and returns a connection object and cursor object
    """
    # Check if the database file exists
    if not os.path.exists("obama.db"):
        # Connect to SQLite database (creates a new file if it doesn't exist)
        conn = sqlite3.connect("obama.db")
        cursor = conn.cursor()

        # Create the counters table
        cursor.execute(
            """
            CREATE TABLE counters (
                id INTEGER PRIMARY KEY,
                name_of_counter TEXT NOT NULL,
                tally_counter INTEGER NOT NULL
            )
        """
        )

        # Commit the changes
        conn.commit()

    else:
        # If the database file exists, connect to it
        conn = sqlite3.connect("obama.db")
        cursor = conn.cursor()

    return conn, cursor


async def setup(bot):
    await bot.add_cog(Counter(bot))
