import os

import psycopg2
from psycopg2 import pool

from .logging_config import create_new_logger

logger = create_new_logger(__name__)

# PostgreSQL connection parameters from environment
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "obamabot")
DB_USER = os.getenv("DATABASE_USER", "obamabot")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

# Connection pool for better performance
connection_pool = None


def initialize_connection_pool():
    """Initialize PostgreSQL connection pool."""
    global connection_pool
    try:
        connection_pool = pool.SimpleConnectionPool(
            1,  # Minimum connections
            5,  # Maximum connections
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        logger.info(
            "PostgreSQL connection pool initialized | Host: %s:%s | Database: %s",
            DB_HOST,
            DB_PORT,
            DB_NAME,
        )
    except psycopg2.Error as e:
        logger.error("Failed to initialize connection pool: %s", e)
        raise


def get_database_connection():
    """
    Get a connection from the pool.
    Returns a psycopg2 connection object.
    """
    if connection_pool is None:
        initialize_connection_pool()

    try:
        conn = connection_pool.getconn()
        logger.debug("Database connection acquired from pool")
        return conn

    except psycopg2.Error as e:
        logger.error("Failed to get database connection: %s", e)
        raise


def return_database_connection(conn):
    """Return a connection to the pool."""
    if connection_pool is not None:
        try:
            connection_pool.putconn(conn)
            logger.debug("Database connection returned to pool")
        except psycopg2.Error as e:
            logger.error("Failed to return connection to pool: %s", e)


def initialize_database():
    """
    Initialize the database by executing the init_create.sql script.
    Creates tables if they don't already exist.
    """
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        # Read the SQL initialization file
        with open("./database/init_create.sql", "r", encoding="UTF-8") as sql_file:
            sql_script = sql_file.read()

        # Execute the SQL script
        cursor.execute(sql_script)
        conn.commit()

        logger.info("Database initialized successfully")
        cursor.close()
        return_database_connection(conn)

    except psycopg2.OperationalError as e:
        if "already exists" in str(e):
            logger.warning("Tables already exist. Skipping setup.")
        else:
            logger.error("Operational error initializing database: %s", e)
            raise

    except (FileNotFoundError, psycopg2.Error) as e:
        logger.error("Error initializing database: %s", e)
        raise


def close_all_connections():
    """Close all connections in the pool."""
    global connection_pool
    if connection_pool:
        try:
            connection_pool.closeall()
            connection_pool = None
            logger.info("All database connections closed")
        except psycopg2.Error as e:
            logger.error("Error closing connections: %s", e)
