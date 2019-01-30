import os
from pathlib import Path
import shutil
import unittest

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
        cls.yaml = create_yaml()
        cls.dao = create_dao(cls.yaml)
        cls.dao.load_data()
        delete_temp_folders()

