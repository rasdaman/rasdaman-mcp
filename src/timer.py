import logging
import time


class Timer:
    """Simple timer for logging execution time."""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()

    @property
    def elapsed(self):
        """Return elapsed time."""
        if self.start_time is None:
            return None
        end = self.end_time if self.end_time is not None else time.time()
        return end - self.start_time

    def log(self, msg=""):
        """Log message appended with 'in Xs'."""
        if self.start_time is None:
            return
        elapsed = self.elapsed
        full_msg = f"{msg} in {elapsed:.3f}s"
        logging.info(full_msg)
