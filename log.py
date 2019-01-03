import logging

LEVELS = {
    'DEBUG': logging.DEBUG,
    'CRITICAL': logging.CRITICAL,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING
}


def __get_formatter():
    return logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def __file_handler(file_name, formatter):
    handler = logging.FileHandler(file_name)
    handler.setFormatter(formatter)
    return handler


def logger(name, file_name, log_level='DEBUG'):
    """
    :param name: logger name type <str>
    :param file_name: file for log info type <str>
    :param log_level: type logging type <str>
    :return: logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(LEVELS.get(log_level))
    formatter = __get_formatter()
    handler = __file_handler(file_name, formatter)
    logger.addHandler(handler)
    return logger
