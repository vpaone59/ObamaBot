import sqlite3
from pathlib import Path

from logging_config import create_new_logger

logger = create_new_logger(__name__)
DATABASE_PATH = Path("./database/bot.db").resolve()


def get_database_connection():
    """
    Connect to the SQLite database using the path from environment variables.
    Returns a connection object.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logger.info("Connected to database at %s", DATABASE_PATH)
        return conn

    except sqlite3.Error as e:
        logger.error("Failed to connect to database: %s", e)
        raise e


def initialize_database():
    """
    Initialize the database with the required tables using the init_create.sql file.
    """
    try:
        if not Path(DATABASE_PATH).exists():
            logger.info("Database file does not exist. Creating now...")

            # Create the database file
            with sqlite3.connect(DATABASE_PATH) as conn:
                logger.info("Database file created successfully")

            conn.close()

        else:
            logger.info("Database file already exists")

    except Exception as e:
        logger.error("Failed to create database file: %s", e)
        raise e

    # Read the SQL initialization file
    with open("./database/init_create.sql", "r", encoding="UTF-8") as sql_file:
        sql_script = sql_file.read()

    # Execute the SQL script
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        logger.info("Database initialized successfully")

    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            logger.warning("Tables already exist. Skipping setup.")
        else:
            logger.error("Failed to initialized database: %s", e)
            raise e

    except sqlite3.Error as e:
        logger.error("Failed to initialized database: %s", e)
        raise e

    finally:
        if conn:
            conn.close()
