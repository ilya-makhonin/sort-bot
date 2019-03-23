import logging
import os

LEVELS = {
    'DEBUG': logging.DEBUG,
    'CRITICAL': logging.CRITICAL,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}


def __get_formatter():
    return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def __file_handler(file_name, formatter):
    if not os.path.exists('logs/'):
        os.mkdir('./logs/')
    _handler = logging.FileHandler(file_name)
    _handler.setFormatter(formatter)
    return _handler


def logger(name, file_name, log_level='DEBUG'):
    """
    :param name: logger name type <str>
    :param file_name: file for log info type <str>
    :param log_level: type logging type <str>
    :return: logger object
    """
    if not os.path.exists('logs/'):
        os.mkdir('./logs/')
    _logger = logging.getLogger(name)
    _logger.setLevel(LEVELS.get(log_level))
    formatter = __get_formatter()
    handler = __file_handler(file_name, formatter)
    _logger.addHandler(handler)
    return _logger
