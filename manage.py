#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from CryptoCharts.src.base import configure_logger
from CryptoCharts.src.backend import worker_daemon_thread,\
    initial_actions

def main():

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webpage.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if len(sys.argv) > 1: # execute the command from the command line
        execute_from_command_line(sys.argv)
    else:
        # execute the runserver command, with --noreload
        # reloading causes the code to be executed twice, for the time being --noreload is a must !
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5578', '--noreload'])


if __name__ == '__main__':
    configure_logger()
    initial_actions()
    worker_daemon_thread().start_all_threads()
    main()