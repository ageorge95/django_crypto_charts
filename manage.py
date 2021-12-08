#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from main._00_base import configure_logger

def main():

    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_crypto_charts.settings')
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
        execute_from_command_line(['manage.py', 'runserver', '5578', '--noreload'])


if __name__ == '__main__':
    os.system('color')
    configure_logger()
    main()