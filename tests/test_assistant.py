import os
from pathlib import Path
from ruamel.yaml import YAML
import unittest
import shutil

from kita.assistant import Assistant
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

class TestAssistant(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.yaml = create_yaml()
        cls.dao = create_dao(cls.yaml)
        cls.dao.load_data()
        cls.assistant = Assistant(cls.yaml, cls.dao)
        delete_temp_folders()

    def tearDown(self):
        delete_temp_folders()

    def test_same_folder_name_and_course_name_should_be_detected(self):
        folder_name = "Lineare Algebra 1"
        course_name = "Lineare Algebra 1"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_name_except_folder_suffix_should_be_detected(self):
        folder_name = "Lineare Algebra I"
        course_name = "Lineare Algebra 1"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_name_except_course_suffix_should_be_detected(self):
        folder_name = "Lineare Algebra 1"
        course_name = "Lineare Algebra I"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_key_should_be_detected(self):
        folder_name = "LA"
        course_key = "la"
        course_name = "Doesn't matter"
        self.assertTrue(self.assistant.are_similar(folder_name, course_key, course_name))

    def test_assignments_sub_folder_should_be_detected(self):
        folder_name = "Course Folder"
        sub_folders = ["Some subfolder", "/!\\ 234", "_doesnt__matter", "Übungen"]
        expected_path = os.path.join(folder_name, "Übungen")
        self.assertEqual(self.assistant.found_assignments_sub_folder(folder_name, sub_folders), expected_path)

    def test_assignments_sub_folder_substring_should_be_detected(self):
        folder_name = "Course Folder"
        sub_folders = ["GBI-Übungen"]
        expected_path = os.path.join(folder_name, "GBI-Übungen")
        self.assertEqual(self.assistant.found_assignments_sub_folder(folder_name, sub_folders), expected_path)

    def test_kit_folder_should_be_detected_no_subfolders(self):
        course_folder = "Programmieren"
        sub_folders = ["Irrelevant subfolders", "", "somefile.txt"]
        expected_result = {'course_key' : 'prg', 'folder_name' : 'Programmieren'}
        self.assertEqual(self.assistant.search_for_assignments_folder(course_folder, sub_folders), expected_result)

    def test_kit_folder_should_be_detected_with_subfolders(self):
        course_folder = "Programmieren"
        sub_folders = ["Some folder", "", "somefile.txt", "Übungen"]
        expected_result = {'course_key' : 'prg', 'folder_name' : 'Programmieren\\Übungen'}
        self.assertEqual(self.assistant.search_for_assignments_folder(course_folder, sub_folders), expected_result)

    def test_kit_folder_should_be_detected_long_path_name_with_subfolders(self):
        course_folder = "Höhere Mathematik 1"
        sub_folders = ["Some folder", "", "somefile.txt", "Übungsblätter"]
        expected_result = {'course_key' : 'hm', 'folder_name' : 'Höhere Mathematik 1\\Übungsblätter'}
        self.assertEqual(self.assistant.search_for_assignments_folder(course_folder, sub_folders), expected_result)

    def test_create_empty_download_folder(self):
        assignment_folders = ["Course A", "Course B", "Course C"]
        root_path = os.path.dirname(__file__)
        expected_folder = os.path.join(root_path, "Downloads")
        self.assistant.create_download_folder(assignment_folders, root_path)
        self.assertTrue(os.path.exists(expected_folder))

    def test_create_download_folder_should_create_course_subfolders(self):
        assignment_folders = ["la", "hm"]
        root_path = os.path.dirname(__file__)
        self.assistant.create_download_folder(assignment_folders, root_path)
        expected_la_folder = os.path.join(root_path, "Downloads", self.full_course_name('la'))
        expected_hm_folder = os.path.join(root_path, "Downloads", self.full_course_name('hm'))
        self.assertTrue(os.path.exists(expected_la_folder))
        self.assertTrue(os.path.exists(expected_hm_folder))

    def test_create_download_folder_should_create_course_subfolders_slash_in_course_name(self):
        assignment_folders = ["gbi"]
        root_path = os.path.dirname(__file__)
        self.assistant.create_download_folder(assignment_folders, root_path)
        expected_course_name = self.full_course_name('gbi').replace('/', '-')
        expected_gbi_folder = os.path.join(root_path, "Downloads", expected_course_name)
        self.assertTrue(os.path.exists(expected_gbi_folder))

    def full_course_name(self, course_key):
        return self.dao.config_data[course_key]['name']

