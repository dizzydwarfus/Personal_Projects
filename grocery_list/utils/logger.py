import logging


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers to avoid duplicate logging.
    if not logger.hasHandlers():
        # Create a file handler
        handler = logging.FileHandler('ah-groceries.log')
        handler.setLevel(logging.DEBUG)

        # Create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

    return logger
