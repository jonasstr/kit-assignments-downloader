import unittest

from kita.core import Scraper

def create_dao(yaml):
    gecko_path = os.path.join(Path(__file__).parents[1], "geckodriver.exe")
    dao = Dao(gecko_path, "data/mock_user.yml", "data/mock_config.yml", yaml)
    return dao

def create_yaml():
    yaml = YAML(typ='rt')
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.compact(seq_seq=False, seq_map=False)
    return yaml

class TestCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.yaml = create_yaml()
        cls.dao = create_dao(cls.yaml)
        cls.dao.load_data()
        cls.scraper = Scraper(None, cls.dao)

    def test_detect_assignment_format(self):
        assignment_files = ['AB-01', 'AB-03', 'AB-04']
