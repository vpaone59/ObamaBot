import logging
from datetime import datetime
import pytz
import os

# Create the log file and directory if it doesn't already exist
log_dir = "./logs"
log_file = os.path.join(log_dir, "bot.log")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(log_file):
    with open(log_file, "w+"):
        pass


def setup_logging(logger_name=__name__, log_file="./logs/bot.log"):
    """
    Configures a logger for the bot.
    """
    # Check if logger with specified name already exists
    if logger_name in logging.Logger.manager.loggerDict:
        return logging.getLogger(logger_name)

    # Create a logger with the name of the module passed in
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Adjust time zone to EST for more accurate logging
    est = pytz.timezone("US/Eastern")
    formatter.converter = lambda *args: datetime.now(est).timetuple()

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a stream handler for logging to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
