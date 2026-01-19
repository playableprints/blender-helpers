"""
benchmark.py - Simple timing helpers
"""

import time


def benchmark_start():
    """Start a benchmark timer."""
    return time.time()


def benchmark_log(start_time, message):
    """Log elapsed time since start_time and return new timestamp."""
    elapsed = time.time() - start_time
    print(f"{message}: {elapsed:.2f}s")
    return time.time()
