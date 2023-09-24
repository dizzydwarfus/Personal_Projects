from setuptools import find_packages, setup
import logging

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    description='Familiarizing with langchain',
    author='DizzyDwarfus',
    license='MIT',
)


# Function to set up the logger
def setup_logger(name, log_file, level=logging.DEBUG):
    """Function to set up as many loggers as you want."""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid setting up the logger again if it already has handlers (to avoid duplicate logs)
    if not logger.hasHandlers():
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create a file handler and set level to debug
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # Create a stream handler (for console) and set level to debug
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
