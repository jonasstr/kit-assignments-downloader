import io
import os
from pathlib import Path
import shutil
import unittest
import unittest.mock as mock

from ruamel.yaml import YAML

from kita.dao import Dao


def create_dao(yaml):
    gecko_path = os.path.join(Path(__file__).parents[1], "geckodriver.exe")
    dao = Dao(gecko_path, "data/mock_user.yml", "data/mock_config.yml", yaml)
    return dao

def create_yaml():
    yaml = YAML(typ='rt')
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.compact(seq_seq=False, seq_map=False)
    return yaml

def delete_temp_folders():
    shutil.rmtree(os.path.join(os.path.dirname(__file__), "Downloads"), ignore_errors=True)


class BaseUnitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_path = os.path.dirname(__file__)
        cls.yaml = create_yaml()
        cls.dao = create_dao(cls.yaml)
        cls.dao.load_data()
        delete_temp_folders()

    def assert_print_once_called_running(self, msg, mock_print):
        mock_print.assert_called_once_with("\r" + msg, end="", flush=True)

    def assert_print_not_called(self, mock_print):
        mock_print.assert_not_called()

    def full_course_name(self, course_key):
        return self.dao.config_data[course_key]['name']

