import unittest.mock as mock

from selenium.common.exceptions import TimeoutException

from kita.misc.logger import ProgressLogger, SilentProgressLogger
from tests.base import BaseUnitTest


class TestLogger(BaseUnitTest):
    @mock.patch("builtins.print")
    def test_silent_logger_single_update(self, mock_print):
        with SilentProgressLogger("LA") as logger:
            logger.update(1)
            self.assert_print_once_called_running("Updating LA: 1..", mock_print)

    @mock.patch("builtins.print")
    def test_silent_logger_multiple_updates(self, mock_print):
        with SilentProgressLogger("LA") as logger:
            logger.update(1)
            logger.update(2)
            self.assert_print_called_running("Updating LA: 1, 2..", mock_print)

    @mock.patch("builtins.print")
    def test_silent_logger_done(self, mock_print):
        with SilentProgressLogger("LA") as logger:
            logger.update(1)
        self.assert_print_called_done("\rUpdating LA: 1, done.", mock_print)

    @mock.patch("builtins.print")
    def test_silent_logger_exception_during_second_update_should_be_handled(self, mock_print):
        try:
            with SilentProgressLogger("LA") as logger:
                logger.update(1)
                logger.update(2)
                raise TimeoutException("indicating assignment 2 could not be found.")
        except TimeoutException:
            self.assert_print_called_done("\rUpdating LA: 1, done.", mock_print)

    @mock.patch("builtins.print")
    def test_silent_logger_exception_during_first_update_should_print_up_to_date(self, mock_print):
        try:
            with SilentProgressLogger("LA") as logger:
                logger.update(1)
                raise TimeoutException("indicating assignments are already up to date.")
        except TimeoutException:
            self.assert_print_called_done("\rUpdating LA: already up to date.", mock_print)

    @mock.patch("builtins.print")
    def test_progress_logger_single_update(self, mock_print):
        with ProgressLogger("LA", "Blatt$$") as logger:
            logger.update(1)
            self.assert_print_once_called_running("Downloading 'Blatt01' from LA", mock_print)

    @mock.patch("builtins.print")
    def test_progress_logger_multiple_updates(self, mock_print):
        with ProgressLogger("LA", "Blatt$$") as logger:
            logger.update(1)
            self.assert_print_called_running("Downloading 'Blatt01' from LA", mock_print)
            logger.update(2)
            self.assert_print_called_running("Downloading 'Blatt02' from LA", mock_print)

    @mock.patch("builtins.print")
    def test_progress_logger_done(self, mock_print):
        with ProgressLogger("LA", "Blatt$$") as logger:
            logger.update(1)
            logger.update(2)
        self.assert_print_called_done(", done.", mock_print)
