from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


class StaticLogger:
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        print(self.msg)

    def __exit__(self, exc_type, exc_value, tb):
        pass


class StrictStaticLogger(StaticLogger):
    def __init__(self, msg, verbose):
        super().__init__(msg)
        self.verbose = verbose

    def __enter__(self):
        if self.verbose:
            super().__enter__()


def strict(msg, verbose):
    return StrictStaticLogger(msg, verbose)


class BaseProgressLogger:
    def __enter__(self):
        return self

    def update(self, msg):
        print("\r" + msg, end="", flush=True)


class StateLogger(BaseProgressLogger):
    def __init__(self, msg):
        super().update(msg)

    def __exit__(self, exc_type, exc_value, tb):
        if isinstance(exc_value, TimeoutException):
            print(", not found.", end="\n", flush=False)
        else:
            print(", done.", end="\n", flush=False)


def state(msg):
    return StateLogger(msg)


class ProgressLogger(StateLogger):
    def __init__(self, course, rename_format):
        self.course = course
        self.rename_format = rename_format

    def update(self, progress):
        num_digits = self.rename_format.count("$")
        assignment = self.rename_format.replace("$" * num_digits, str(progress).zfill(num_digits))
        super().update("Downloading '{}' from {}".format(assignment, self.course))


class SilentProgressLogger(BaseProgressLogger):
    def __init__(self, course):
        self.course = course
        self.prev_output = None
        self.latest_output = None

    def update(self, progress):
        if self.latest_output:
            progress = "{}, {}".format(self.latest_output, progress)
            self.prev_output = self.latest_output
        super().update("Updating {}: {}..".format(self.course, progress))
        self.latest_output = progress

    def __exit__(self, exc_type, exc_value, tb):
        from kit-dl.core import LoginException

        if exc_type in (TimeoutException, NoSuchElementException) and self.prev_output is None:
            print("\rUpdating {}: already up to date.".format(self.course), flush=False, end="\n")
        elif exc_type is LoginException:
            print("\rUpdating {}, cancelled!".format(self.course), flush=False, end="\n")
        else:
            output = self.prev_output if self.prev_output else self.latest_output
            print("\rUpdating {}: {}, done.".format(self.course, output), flush=False, end="\n")
