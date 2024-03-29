"""
Counter Cog for ObamaBot by Vincent Paone https://github.com/vpaone59

This Cog is custom made for a specific server and will not work in normal servers.
"""

from discord.ext import commands
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
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
        print(f'{self} ready')
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
                db_conn, db_cursor = connect_db()
                db_cursor.execute(
                    f"UPDATE counters SET tally_counter=tally_counter + 1 WHERE name_of_counter = '{cap_message}'")
                db_conn.commit()
            except Exception as err:
                await message.channel.send("Something went wrong: {}".format(err))
            finally:
                db_cursor.close()
                db_conn.close()
        else:
            return

    @commands.command(aliases=['reset'], description='Resets the tally for a given *tracker*')
    @commands.has_permissions(administrator=True)
    async def reset_tally(self, ctx, counter_name):
        """
        Resets tally_counter to zero for a user input tracker_name
        """
        sql = "UPDATE counters SET tally_counter=0 WHERE name_of_counter = %s"
        val = counter_name
        try:
            db_conn, db_cursor = connect_db()
            db_cursor.execute(sql, (val,))
            db_conn.commit()
            await ctx.send(f"```success. {counter_name} is now 0```")
        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            db_cursor.close()
            db_conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_counter(self, ctx, counter_name):
        """
        Create an entry in the Database to keep a tally of
        """
        sql = "INSERT INTO counters (id, name_of_counter, tally_counter) VALUES (id, %s, %s)"
        val = (counter_name, 0)
        try:
            db_conn, db_cursor = connect_db()
            db_cursor.execute(sql, val)
            db_conn.commit()
            await ctx.send(f"```success. {counter_name} is now being counted!```")
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            db_cursor.close()
            db_conn.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delete_counter(self, ctx, counter_name):
        """
        Delete an entry in the Database
        """
        sql = "DELETE FROM counters WHERE name_of_counter = %s"
        # must be a list, tuple or dict because of how create_counter is entered
        # we opt for tuple here with the second value left empty
        val = (counter_name,)
        try:
            db_conn, db_cursor = connect_db()
            db_cursor.execute(sql, val)
            db_conn.commit()
            await ctx.send(f"```success. {counter_name} has now been deleted!```")
            get_counters()

        except Exception as err:
            await ctx.send("Something went wrong: {}".format(err))
        finally:
            db_cursor.close()
            db_conn.close()

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
                counter_string += f'{c_name}\t-\t{str(c_tally)}\n'

            await ctx.send(f'```{counter_string}```')
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
    db_conn, db_cursor = connect_db()

    try:
        db_cursor.execute(
            "SELECT name_of_counter, tally_counter FROM counters")
        rows = db_cursor.fetchall()

        for row in rows:
            counter_names.append(row[0])
            counters_from_db.append([row[0], row[1]])
    except Exception as err:
        print("Something went wrong: {}".format(err))
    finally:
        db_cursor.close()
        db_conn.close()


def connect_db():
    """
    Function that connects to the database and returns a connection object and cursor object
    """
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("PASSWORD"),
            database=os.getenv("TARGET"))
        my_cursor = mydb.cursor()
        
        return mydb, my_cursor
    
    except Exception as err:
        print("Something went wrong: {}".format(err))
        return 200

async def setup(bot):
    await bot.add_cog(Counter(bot))
