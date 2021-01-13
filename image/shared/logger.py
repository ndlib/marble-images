from . import config


def info(msg):
    if config.LOG_INFO:
        print(msg, flush=True)


def debug(msg):
    if config.LOG_DEBUG:
        print(msg, flush=True)


def error(msg):
    if config.LOG_ERROR:
        print(msg, flush=True)
