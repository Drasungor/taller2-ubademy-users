import requests


API_URL = 'https://log-api.newrelic.com/log/v1'


class NewrelicLogger:
    def __init__(self, api_key):
        self.api_key = api_key

    def info(self, message):
        info_message = f'[INFO]: {message}'
        self.__forward_log(info_message)

    def warning(self, message):
        warning_message = f'[WARNING]: {message}'
        self.__forward_log(warning_message)

    def error(self, message):
        error_message = f'[ERROR]: {message}'
        self.__forward_log(error_message)

    def debug(self, _message):
        pass

    def __forward_log(self, message):
        payload = {
            'message': message,
        }

        headers = {
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }

        requests.post(API_URL, json=payload, headers=headers)
