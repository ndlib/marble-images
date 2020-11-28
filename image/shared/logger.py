from . import config


def log(msg):
    if config.LOG_INFO:
        print(msg)


def debug(msg):
    if config.LOG_DEBUG:
        print(msg)


def error(msg):
    if config.LOG_ERROR:
        print(msg)
