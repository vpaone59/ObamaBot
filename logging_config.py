import logging


def setup_logging():
    """Configures logging for the bot."""
    LOG_FILE = "bot.log"

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    # Create a logger with the name of the main module
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # Optionally, add a stream handler for logging to the console
    # stream_handler = logging.StreamHandler()
    # logger.addHandler(stream_handler)


if __name__ == "__main__":
    setup_logging()
