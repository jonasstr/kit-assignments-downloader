from kita.core import Scraper
from tests.base import BaseUnitTest
 

class TestCore(BaseUnitTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scraper = Scraper(None, cls.dao)

    def test_detect_assignment_format(self):
        assignment_files = ['some_file.py', 'AB-01.pdf']
        self.assertEqual(self.scraper.detect_assignment_format(assignment_files), 'AB-$$')
