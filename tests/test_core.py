from kita.core import Scraper
from tests.base import BaseUnitTest
 

class TestCore(BaseUnitTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scraper = Scraper(None, cls.dao)

    def test_format_assignment_name_leading_zero(self):
        format = 'Blatt_$$'
        self.assertEqual(self.scraper.format_assignment_name(format, 1), 'Blatt_01')

    def test_format_assignment_name_digit_overflow(self):
        format = 'Blatt_$'
        self.assertEqual(self.scraper.format_assignment_name(format, 10), 'Blatt_10')

    def test_detect_assignment_format(self):
        assignment_files = ['some_file.py', 'AB-01.pdf']
        self.assertEqual(self.scraper.detect_format(assignment_files), 'AB-$$')

    def test_find_latest_assignment(self):
        assignment_files = ['Blatt-05.pdf', 'Blatt-01.pdf', 'Blatt-08.pdf', 'Blatt-06.pdf']
        self.assertEqual(self.scraper.latest_assignment(assignment_files, 'Blatt-$$'), 8)

    def test_find_latest_assignment_two_digit_num(self):
        assignment_files = ['Blatt-05.pdf', 'Blatt-10.pdf']
        self.assertEqual(self.scraper.latest_assignment(assignment_files, 'Blatt-$$'), 10)

