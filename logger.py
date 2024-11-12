import logging
import logging.handlers

def set_logger():
    logger = logging.getLogger()

    stream_handler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        filename="./logs/application.log",
        maxBytes=100000,
        backupCount=5,
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s| %(levelname)-5s | %(name)s.%(funcName)s.%(lineno)d | %(message)s"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
