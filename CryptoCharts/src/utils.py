from datetime import datetime
from logging import getLogger
from multiprocessing import Manager,\
    Queue
from time import sleep
from sys import stdin

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