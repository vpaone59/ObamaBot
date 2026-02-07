"""
https://github.com/vpaone59

This module configures a logger for the bot. The logger logs to a file and the console.
"""

import json
import logging
import os
from datetime import datetime

import pytz

# Create the log file and directory if it doesn't already exist
LOG_DIR = "./logs"
log_file_path = os.path.join(LOG_DIR, "bot.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if not os.path.exists(log_file_path):
    with open(log_file_path, "w+", encoding="utf-8"):
        pass


class JsonFormatter(logging.Formatter):
    """
    Custom formatter for logging in JSON format.
    """

    def format(self, record):
        log_record = {
            "asctime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": record.name,
            "levelname": record.levelname,
            "message": record.getMessage(),
        }
        # Adjust time zone to EST for more accurate logging
        est = pytz.timezone("US/Eastern")
        log_record["asctime"] = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps(log_record)


def create_new_logger(logger_name=__name__, log_file="./logs/bot.log"):
    """
    Create a new logger with the specified name and log file.
    """
    # Check if logger with specified name already exists
    if logger_name in logging.Logger.manager.loggerDict:
        return logging.getLogger(logger_name)

    # Create a logger with the name of the module passed in
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create a handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    json_formatter = JsonFormatter()
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # Create a handler for logging to stdout
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    return logger
