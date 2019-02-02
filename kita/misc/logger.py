from logging.handlers import RotatingFileHandler
from selenium.common.exceptions import TimeoutException

from kita.misc import utils


class ProgressBar:
    def __init__(self, message, silent=False, show_done=False):
        self.silent = silent
        if not self.silent:
            self.output = "\r" + utils.reformat(message["verbose"])
            self.done = ", done." if show_done else ""
            print(self.output, end="", flush=True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if not self.silent:
            if isinstance(exc_value, TimeoutException):
                self.done = ", cancelled!"
            print(self.done, end="\n", flush=False)


class StrictLogger:
    def __init__(self, msg, verbose, show_done):
        self.verbose = verbose
        if self.verbose:
            self.done = ", done" if show_done else ""
            self.output = "\r" + utils.reformat(msg)
            print(self.output, end="", flush=True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if isinstance(exc_value, TimeoutException):
            self.done = ", cancelled!"
        if self.verbose:
            print(self.done, end="\n", flush=False)


class BaseLogger:
    def __init__(self, msg, verbose, show_done):
        self.output = "\r" + utils.reformat(msg)
        self.verbose = verbose
        self.done = ", done" if show_done else ""
        print(self.output, end="", flush=True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if hasattr(self, "done"):
            if isinstance(exc_value, TimeoutException):
                self.done = ", cancelled!"
            print(self.done, end="\n", flush=False)


class StrictLogger(BaseLogger):
    def __init__(self, msg, verbose, show_done):
        if verbose:
            super().__init__(msg, verbose, show_done)


class SilentLogger(BaseLogger):
    def __init__(self, verbose_msg, silent_msg, verbose, show_done):
        super().__init__(verbose_msg if verbose else silent_msg, verbose, show_done)


def bar(message, silent=False, show_done=False):
    return ProgressBar(message, silent, show_done)


def strict(msg, verbose=False, show_done=False):
    return StrictLogger(msg, verbose, show_done)


def silent(verbose_msg, silent_msg, verbose=False, show_done=False):
    return SilentLogger(verbose_msg, silent_msg, verbose, show_done)
