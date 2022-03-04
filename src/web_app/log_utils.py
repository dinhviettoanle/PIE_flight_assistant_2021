"""
Utils for logs
"""

import time
import functools
from datetime import datetime

# ================== LOGGING UTILS ===================

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_info(*args, **kwargs):
    # print(args, flush=True)
    return

def fprint(*args, **kwargs):
    print(args, flush=True, **kwargs)

def print_error(*args, **kwargs):
    print(f"{bcolors.FAIL}[{datetime.now()}]: {args}{bcolors.ENDC}", flush=True)

def print_event(*args, **kwargs):
    print(f"{bcolors.OKBLUE}[{datetime.now()}]:{args}{bcolors.ENDC}", flush=True)


def timeit(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print_event(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value
    return wrapper_timer
