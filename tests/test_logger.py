from kita.misc import logger
from tests.base import BaseUnitTest

import sys
import unittest.mock as mock

from tests.base import BaseUnitTest

class TestLogger(BaseUnitTest):

    @mock.patch("builtins.print")
    def test_strict_log_should_print_when_verbose(self, mock_print):
        with logger.strict("Message", verbose=True):
            self.assert_print_once_called_running("Message", mock_print)

    @mock.patch("builtins.print")
    def test_strict_log_should_not_print_when_silent(self, mock_print):
        with logger.strict("Message", verbose=False):
            self.assert_print_not_called(mock_print)

    @mock.patch("builtins.print")
    def test_silent_log_should_print_silent_msg_when_silent(self, mock_print):
        with logger.silent("Verbose message", "Silent message", verbose=False):
            self.assert_print_once_called_running("Silent message", mock_print)

    @mock.patch("builtins.print")
    def test_silent_log_should_print_verbose_msg_when_verbose(self, mock_print):
        with logger.silent("Verbose message", "Silent message", verbose=True):
            self.assert_print_once_called_running("Verbose message", mock_print)

