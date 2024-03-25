import logging


def setup_logging(log_file="/logs/bot.log"):
    """
    Configures a logger for the bot.
    """
    # Create a logger with the name of the main module
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Set the logging level to INFO

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create a stream handler for logging to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Logging configured successfully.")
