from sys import stdout
from datetime import datetime
from logging import getLogger
from logging import basicConfig,\
    INFO, DEBUG, WARNING, ERROR, CRITICAL,\
    Formatter,\
    StreamHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler
from multiprocessing import Manager
from os import system

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):

        if 'shared_cache' not in cls._instances.keys():
            cls._instances['shared_cache'] = Manager().dict()

        if cls not in cls._instances:

            cls.shared_cache = cls._instances['shared_cache']

            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ContextMenuBase():

    def __enter__(self):
        self.exec_starttime = datetime.now()

        self._log = getLogger()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._log.info('Execution of {} took {}'.format(type(self).__name__,
                                                        datetime.now() - self.exec_starttime))

def configure_logger(basename : str = "runtime_log.log"):
    system('color')
    class CustomFormatter(Formatter):
        grey = "\x1b[38;21m"
        yellow = "\x1b[33;21m"
        red = "\x1b[31;21m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = '%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineno)d -> %(name)s - %(funcName)s] ___ %(message)s'

        FORMATS = {
            DEBUG: grey + format + reset,
            INFO: grey + format + reset,
            WARNING: yellow + format + reset,
            ERROR: red + format + reset,
            CRITICAL: bold_red + format + reset
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = Formatter(log_fmt)
            return formatter.format(record)

    ch = StreamHandler(stream=stdout)
    ch.setLevel(DEBUG)
    ch.setFormatter(CustomFormatter())
    fh = ConcurrentRotatingFileHandler(basename,
                                       mode='a',
                                       maxBytes=20*1024*1024,
                                       backupCount=2)
    fh.setLevel(DEBUG)
    fh.setFormatter(Formatter('%(asctime)s,%(msecs)d %(levelname)-4s [%(filename)s:%(lineno)d -> %(name)s - %(funcName)s] ___ %(message)s'))

    basicConfig(datefmt='%Y-%m-%d:%H:%M:%S',
                level=INFO,
                handlers=[fh,ch])