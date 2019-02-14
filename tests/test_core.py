from kit_dl.core import Scraper
from tests.base import BaseUnitTest


class TestCore(BaseUnitTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scraper = Scraper(None, cls.dao, True)

    def test_format_assignment_name_leading_zero(self):
        format = "Blatt_$$"
        self.assertEqual("Blatt_01", self.scraper.format_assignment_name(format, 1))

    def test_format_assignment_name_digit_overflow(self):
        format = "Blatt_$"
        self.assertEqual("Blatt_10", self.scraper.format_assignment_name(format, 10))

    def test_detect_assignment_format(self):
        assignment_files = ["some_file.py", "AB-01.pdf"]
        self.assertEqual("AB-$$", self.scraper.detect_format(assignment_files))

    def test_invalid_assignment_format_should_not_be_detected(self):
        assignment_files = ["some_file.py", "not_an_assignment.pdf"]
        self.assertIsNone(self.scraper.detect_format(assignment_files))

    def test_find_latest_assignment(self):
        assignment_files = ["Blatt-05.pdf", "Blatt-01.pdf", "Blatt-08.pdf", "Blatt-06.pdf"]
        self.assertEqual(8, self.scraper.get_latest_assignment(assignment_files, "Blatt-$$"))

    def test_find_latest_assignment_two_digit_num(self):
        assignment_files = ["Blatt-05.pdf", "Blatt-10.pdf"]
        self.assertEqual(10, self.scraper.get_latest_assignment(assignment_files, "Blatt-$$"))

    def test_on_start_update_latest_assignment_found(self):
        actual = self.scraper.get_on_start_update_msg("la", 9, "Blatt$$")
        self.assertEqual("Updating LA assignments, latest: Blatt09.pdf", actual)

    def test_on_start_update_latest_assignment_not_found_negative(self):
        actual = self.scraper.get_on_start_update_msg("la", -1, "Blatt$$")
        self.assertEqual("No assignments found in LA directory, starting at 1.", actual)

    def test_on_start_update_latest_assignment_not_found_zero(self):
        actual = self.scraper.get_on_start_update_msg("la", 0, "Blatt$$")
        self.assertEqual("No assignments found in LA directory, starting at 1.", actual)
