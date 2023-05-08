#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from os import environ,\
    system
from sys import argv
from threading import Thread
from time import sleep
from CryptoCharts.src.logger import configure_logger
from CryptoCharts.src.backend import worker_daemon_thread,\
    initial_actions
from CryptoCharts.src.config import pairs_to_show

def main(cmd_arguments):
    """Run administrative tasks."""
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(cmd_arguments) > 1: # execute the command from the command line
        execute_from_command_line(cmd_arguments)
    else:
        # migrate is executed always, when the server starts
        execute_from_command_line(['manage.py', 'migrate'])
        # execute the runserver command, with --noreload
        # reloading causes the code to be executed twice, for the time being --noreload is a must !
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5578', '--noreload'])

if __name__ == '__main__':

    # first start the django server
    django_thread = Thread(target=main,
                           args=(argv,))
    django_thread.start()
    sleep(5)

    system('color')
    configure_logger()
    initial_actions(pairs_to_show=pairs_to_show)
    worker_daemon_thread().start_all_threads()