#!/usr/bin/env python3
# coding: utf-8
"""
__description__ = "h1 vulnerability report scrapper"
__course__ = "ics691e"
__organization__ = "Information and Computer Sciences Department, University of Hawai'i at Mānoa"
__author__ = "Craig Opie"
__email__ = "opieca@hawaii.edu"
__version__ = "1.0.0"
__created__ = "2022-10-01"
__modified__ = "2022-10-10"
__maintainer__ = "Craig Opie"
"""
import sys
import time
import threading
from itertools import cycle

class Spinner:
    busy = False
    delay = 0.1

    def __init__(self, delay=None):
        self.spinner = cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        return exc_type is None