import logging

LOG_FILE = "./app/bot.log"


def setup_logging():
    """Configures logging for the bot."""

    # Create a logger with the name of the main module
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    # Optionally, add a stream handler for logging to the console
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)


if __name__ == "__main__":
    setup_logging()
