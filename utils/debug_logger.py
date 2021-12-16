import sys
import logging


def debug_logger():
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('logs.log')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s')

    handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(file_handler)
    return logger
