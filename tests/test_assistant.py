import os

from kit-dl.assistant import Assistant
from tests.base import BaseUnitTest


class TestAssistant(BaseUnitTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.assistant = Assistant(cls.yaml, cls.dao)

    def test_same_folder_name_and_course_name(self):
        folder_name = "Lineare Algebra 1"
        course_name = "Lineare Algebra 1"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_name_except_folder_suffix(self):
        folder_name = "Lineare Algebra I"
        course_name = "Lineare Algebra 1"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_name_except_course_suffix(self):
        folder_name = "Lineare Algebra 1"
        course_name = "Lineare Algebra I"
        self.assertTrue(self.assistant.are_similar(folder_name, None, course_name))

    def test_same_folder_name_and_course_key(self):
        folder_name = "LA"
        course_key = "la"
        course_name = "Doesn't matter"
        self.assertTrue(self.assistant.are_similar(folder_name, course_key, course_name))

    def test_assignments_sub_folder(self):
        folder_name = "Course Folder"
        sub_folders = ["Some subfolder", "/!\\ 234", "_doesnt__matter", "Übungen"]
        expected_path = os.path.join(folder_name, "Übungen")
        self.assertEqual(expected_path, self.assistant.found_assignments_sub_folder(folder_name, sub_folders))

    def test_assignments_sub_folder_substring(self):
        folder_name = "Course Folder"
        sub_folders = ["GBI-Übungen"]
        expected_path = os.path.join(folder_name, "GBI-Übungen")
        self.assertEqual(expected_path, self.assistant.found_assignments_sub_folder(folder_name, sub_folders))

    def test_kit_folder_no_subfolders(self):
        folder_name = "Programmieren"
        sub_folders = ["Irrelevant subfolders", "", "somefile.txt"]
        expected_result = {"course_key": "prg", "folder_name": "Programmieren"}
        self.assertEqual(
            expected_result, self.assistant.search_for_assignments_folder(folder_name, sub_folders)
        )

    def test_kit_folder_with_subfolders(self):
        course_folder = "Programmieren"
        sub_folders = ["Some folder", "", "somefile.txt", "Übungen"]
        expected_result = {"course_key": "prg", "folder_name": os.path.join("Programmieren", "Übungen")}
        self.assertEqual(
            expected_result, self.assistant.search_for_assignments_folder(course_folder, sub_folders)
        )

    def test_kit_folder_long_path_name_with_subfolders(self):
        course_folder = "Höhere Mathematik 1"
        sub_folders = ["Some folder", "", "somefile.txt", "Übungsblätter"]
        expected_result = {
            "course_key": "hm",
            "folder_name": os.path.join("Höhere Mathematik 1", "Übungsblätter"),
        }
        self.assertEqual(
            expected_result, self.assistant.search_for_assignments_folder(course_folder, sub_folders)
        )

    def test_create_empty_download_folder(self):
        assignment_folders = ["Course A", "Course B", "Course C"]
        expected_folder = os.path.join(self.root_path, "Downloads")
        self.assistant.create_download_folder(assignment_folders, self.root_path)
        self.assertTrue(os.path.exists(expected_folder))

    def test_create_download_folder_should_create_course_subfolders(self):
        assignment_folders = ["la", "hm"]
        self.assistant.create_download_folder(assignment_folders, self.root_path)
        expected_la_folder = os.path.join(self.root_path, "Downloads", self.full_course_name("la"))
        expected_hm_folder = os.path.join(self.root_path, "Downloads", self.full_course_name("hm"))
        self.assertTrue(os.path.exists(expected_la_folder))
        self.assertTrue(os.path.exists(expected_hm_folder))

    def test_download_folder_should_create_subfolders_slash_in_course_name(self):
        assignment_folders = ["gbi"]
        self.assistant.create_download_folder(assignment_folders, self.root_path)
        expected_course_name = self.full_course_name("gbi").replace("/", "-")
        expected_gbi_folder = os.path.join(self.root_path, "Downloads", expected_course_name)
        self.assertTrue(os.path.exists(expected_gbi_folder))
