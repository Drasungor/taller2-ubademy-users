from unittest.mock import patch, MagicMock
from utils.newrelic_logger import NewrelicLogger


@patch('utils.newrelic_logger.requests.post')
def test_info_log(mock_newrelic_api):
    mock_newrelic_api.return_value = MagicMock(status_code=200)
    logger = NewrelicLogger('newrelic-api-key')
    logger.info('This is an INFO level log')


@patch('utils.newrelic_logger.requests.post')
def test_info_log(mock_newrelic_api):
    mock_newrelic_api.return_value = MagicMock(status_code=200)
    logger = NewrelicLogger('newrelic-api-key')
    logger.debug('This is an DEBUG level log')


@patch('utils.newrelic_logger.requests.post')
def test_info_log(mock_newrelic_api):
    mock_newrelic_api.return_value = MagicMock(status_code=200)
    logger = NewrelicLogger('newrelic-api-key')
    logger.warning('This is an WARNING level log')


@patch('utils.newrelic_logger.requests.post')
def test_info_log(mock_newrelic_api):
    mock_newrelic_api.return_value = MagicMock(status_code=200)
    logger = NewrelicLogger('newrelic-api-key')
    logger.error('This is an ERROR level log')
