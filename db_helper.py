import os
import sqlite3
from logging_config import create_new_logger
from dotenv import load_dotenv

load_dotenv()

logger = create_new_logger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH")
SQL_INIT_FILE = DATABASE_PATH + "/init_create.sql"
print("SQL_INIT_FILE", SQL_INIT_FILE)


def get_db_connection():
    """
    Connect to the SQLite database using the path from environment variables.
    Returns a connection object.
    """
    if not DATABASE_PATH:
        logger.error("DATABASE_PATH environment variable not set.")
        raise ValueError("DATABASE_PATH environment variable not set.")

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logger.info("Connected to database")
        return conn
    except sqlite3.Error as e:
        logger.error("Failed to connect to database: %s", e)
        raise e


def initialize_db():
    """
    Initialize the database with the required tables using the init_create.sql file.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read the SQL initialization file
    with open(SQL_INIT_FILE, "r") as sql_file:
        sql_script = sql_file.read()

    # Execute the SQL script
    try:
        cursor.executescript(sql_script)
        conn.commit()
        logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error("Failed to initialize database: %s", e)
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_db()
