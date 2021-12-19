import os
from utils.debug_logger import debug_logger
from utils.newrelic_logger import NewrelicLogger


class Logger:
    def __init__(self, api_key):
        if api_key:
            self.logger = NewrelicLogger(api_key)
        else:
            self.logger = debug_logger()

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)


logger = Logger(os.environ.get('NEWRELIC_API_KEY'))
