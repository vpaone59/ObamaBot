import os
import sqlite3
from logging_config import create_new_logger
from dotenv import load_dotenv

load_dotenv()

logger = create_new_logger(__name__)

HOST_DB_PATH = os.getenv("HOST_DB_PATH")
DATABASE_PATH = f"{HOST_DB_PATH}/obamabot.db"
SQL_INIT_FILE = "./database/init_create.sql"


def get_db_connection():
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


def initialize_db():
    """
    Initialize the database with the required tables using the init_create.sql file.
    """
    # Check if the database file exists
    try:
        if not os.path.exists(DATABASE_PATH):
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
    with open(SQL_INIT_FILE, "r") as sql_file:
        sql_script = sql_file.read()

    # Execute the SQL script
    try:
        conn = get_db_connection()
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
