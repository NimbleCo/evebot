import logging

from evebot.settings import config
from termcolor import colored

class ColoredFormatter(logging.Formatter):

    level_mapping = {
        logging.DEBUG: {'attrs': ['dark', 'bold']},
        logging.INFO: {'color': 'blue', 'attrs': ['bold']},
        logging.WARN: {'color': 'yellow', 'attrs': ['bold']},
        logging.ERROR: {'color': 'red', 'attrs': ['bold']},
        logging.CRITICAL: {'color': 'red', 'on_color': 'on_red', 'attrs': ['bold']},
        logging.NOTSET: {}
    }

    def __init__(self, format, datefmt=None, style='%'):
        logging.Formatter.__init__(self, format, datefmt, style)

    def formatMessage(self, record):
        record.levelname = colored(record.levelname, **self.level_mapping[record.levelno])
        record.name = colored(record.name, 'green')
        record.asctime = colored(record.asctime, 'yellow')

        return self._style.format(record)

def init_logging():
    rootLogger = logging.getLogger('')

    if config.DEBUG:
        loglevel = logging.DEBUG
        logformat = '[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s'
    else:
        loglevel = logging.INFO
        logformat = '[%(asctime)s] %(message)s'


    formatter = logging.Formatter(logformat)
    coloredFormatter = ColoredFormatter(logformat)

    rootLogger.setLevel(loglevel)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(loglevel)
    consoleHandler.setFormatter(coloredFormatter)

    rootLogger.addHandler(consoleHandler)

    logfile = config.get_log_file()

    if logfile:
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setLevel(loglevel)
        fileHandler.setFormatter(formatter)

        rootLogger.addHandler(fileHandler)

        rootLogger.debug('Starting logging to "%s".' % logfile)

    if config.DEBUG:
        rootLogger.debug('DEBUG mode is enabled.')

