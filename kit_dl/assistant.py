import getpass
import os

from colorama import Fore, Style
from colorama import init
import click

import kit_dl.misc.utils as utils


class Assistant:
    def __init__(self, yaml, dao):
        # Initialize colorama.
        init()
        self.yaml = yaml
        self.dao = dao

    def echo(self, text, is_prompt=False):
        """Forwards the given text to click.echo() and optionally applies a different style to the text."""
        color = Fore.CYAN if is_prompt else Style.RESET_ALL
        if is_prompt:
            text = "> " + text
        click.echo(color + text)

    def prompt(self, text):
        """Forwards the given text to click.echo() and adds cyan color and a '>' symbol
        to the start of the string.
        """
        return click.prompt(Fore.CYAN + "> " + text)

    def confirm(self, text, default=False):
        suffix = " (Y/n) [y]: " if default else " (y/N) [n]: "
        return click.confirm(
            Fore.CYAN + "> " + text, default=default, show_default=False, prompt_suffix=suffix
        )

    def setup_user(self):
        """Starts the setup assistant for setting up the user.yml file.
        Saves the login credentials of the user and the root path for downloading assignments.
        """
        from tkinter import filedialog

        # user.yml already exists.
        if os.path.isfile(self.dao.user_yml_path):
            if not self.confirm("Kita is already set up. Overwrite existing config?"):
                return False

        self.echo(
            "\nWelcome to the kit-dl setup utility.\n\nPlease enter values for the following "
            "settings (just press Enter to\naccept a default value, if one is given in brackets).\n"
        )

        data = {}
        data["user_name"] = self.prompt("Enter your correct ilias user name").strip()
        data["password"] = self.select_password()
        self.echo(
            "\nChoose a location for saving your assignments. If you already\n"
            "downloaded assignments manually please choose your KIT folder\nfor auto-detection."
        )
        self.echo("Select the root path for your assignments from the dialog window:", is_prompt=True)

        root_path = os.path.abspath(filedialog.askdirectory())
        data["destination"] = {}
        data["destination"]["root_path"] = root_path
        # Set default rename format.
        data["destination"]["rename_format"] = "Blatt$$"
        self.dao.create_user(data)

        self.echo("Saved root folder '{}'.".format(utils.reformat(root_path)))
        return True

    def select_password(self):
        password = getpass.getpass("> Enter your ilias password: ").strip()
        while getpass.getpass("> Please confirm the password: ").strip() != password:
            self.echo("The passwords do not match." + Fore.CYAN)
            password = getpass.getpass("> Enter your ilias password: ").strip()
        return password

    def setup_config(self):
        """Starts the setup assistant for setting up the config.yml file."""
        self.dao.load_config()
        if os.path.isfile(self.dao.user_yml_path):
            self.dao.load_user()
            root_path = self.dao.user_data["destination"]["root_path"]
            if not os.path.isdir(root_path):
                self.echo(
                    "\nKita has not been configured correctly (root_path not found).\n"
                    "Use 'kit-dl setup --user' instead."
                )
                return False

            assignment_folders = self.detected_assignment_folders(root_path)
            added_courses = []
            if assignment_folders:
                added_courses = self.show_kit_folder_detected_dialog(assignment_folders, root_path)
            self.show_confirm_all_courses_dialog(
                (course for course in self.dao.config_data), added_courses, root_path
            )
            return True

    def show_kit_folder_detected_dialog(self, assignment_folders, root_path):
        """Asks the user to confirm the download locations for the given courses."""
        self.echo("\nPossible KIT folder detected:")
        added_courses = []
        for selection in assignment_folders:
            full_path = os.path.join(root_path, selection["folder_name"])
            message = utils.reformat(
                "Save {} assignments to '{}'?".format(selection["course_key"].upper(), full_path)
            )
            if self.confirm(message, default=True):
                added_courses.append(selection["course_key"])
                self.dao.config_data[selection["course_key"]]["path"] = selection["folder_name"]
                self.dao.dump_config()
        return added_courses

    def show_confirm_all_courses_dialog(self, assignment_folders, added_courses, root_path):
        if not added_courses:
            download_dir = self.create_download_folder(assignment_folders, root_path)
            click.echo("Assignments will be saved to '{}'".format(download_dir))
            return
        self.update_selected_courses(added_courses)
        from tkinter import filedialog

        while self.choice and not self.confirm(
            "Are these all courses: {}?".format(self.selected), default=True
        ):
            course_key = self.show_select_folder_manually_dialog(self.choice, "Which courses are missing?")
            selected_path = filedialog.askdirectory()
            self.show_assignments_save_location_dialog(course_key, selected_path)
            added_courses.append(course_key.lower())
            self.update_selected_courses(added_courses)

    def update_selected_courses(self, added_courses):
        self.selected = ", ".join(course.upper() for course in added_courses)
        self.choice = ", ".join(key.upper() for key in self.dao.config_data.keys() if key not in added_courses)

    def show_assignments_save_location_dialog(self, course_key, selected_path):
        self.echo(
            "{} assignments will be saved to '{}'.".format(course_key.upper(), utils.reformat(selected_path))
        )
        self.dao.config_data[course_key]["path"] = selected_path
        self.dao.dump_config()

    def show_select_folder_manually_dialog(self, choice, prompt_msg):
        """Shows the setup dialog for adding the location of additional assignments."""
        course_key = self.prompt("{} Choose from {}".format(prompt_msg, choice))
        while not course_key.lower() in self.dao.config_data.keys():
            self.echo("Error: invalid input")
            course_key = self.prompt("{} Choose from {}".format(prompt_msg, choice))
        self.echo("Choose a location for saving your {} courses:".format(course_key.upper()), is_prompt=True)
        return course_key

    def create_download_folder(self, course_keys, root_path):
        """
        :param course_keys:
        :param root_path:
        """
        download_dir = os.path.join(root_path, "Downloads")
        os.makedirs(download_dir, exist_ok=True)
        for key in course_keys:
            if key in self.dao.config_data:
                new_key = self.dao.config_data[key]["name"].replace("/", "-").replace("\\", "-")
                course_dir = os.path.join(download_dir, new_key)
                os.makedirs(course_dir, exist_ok=True)
                self.dao.config_data[key]["path"] = course_dir
                self.dao.dump_config()
        return download_dir

    def detected_assignment_folders(self, root_path):
        course_folders = next(os.walk(root_path))[1]
        assignment_folders = []
        for folder_name in course_folders:
            sub_folders = next(os.walk(os.path.join(root_path, folder_name)))[1]
            result = self.search_for_assignments_folder(folder_name, sub_folders)
            if result:
                assignment_folders.append(result)
        return assignment_folders

    def search_for_assignments_folder(self, folder_name, sub_folders):
        """Searches for a possible folder containing the assignments based on the folder name."""
        for course_key in self.dao.config_data:
            # Folder has been found.
            if course_key == folder_name.lower() or self.are_similar(
                folder_name, course_key, self.dao.config_data[course_key]["name"]
            ):
                sub_folder_name = self.found_assignments_sub_folder(folder_name, sub_folders)
                return (
                    {"course_key": course_key, "folder_name": sub_folder_name}
                    if sub_folder_name
                    else {"course_key": course_key, "folder_name": folder_name}
                )

    def found_assignments_sub_folder(self, course_folder_name, sub_folders):
        for sub_folder in sub_folders:
            name_list = ["assignments", "blätter", "übungen", "übungsblätter"]
            # Check whether the name of the sub-folder is either one of the above names.
            if any(x in sub_folder.lower() for x in name_list):
                return os.path.join(course_folder_name, sub_folder)

    def are_similar(self, folder_name, course_key, course_name):
        """Checks whether a given folder name is similar to the full name of a config.yml course
                or is equal to the course key (e.g. la)."""
        if (
            folder_name.lower() == course_key
            or folder_name.startswith(course_name)
            or course_name.startswith(folder_name)
        ):
            return True
        course_suffixes = {"I": 1, "II": 2, "III": 3}
        for suffix in course_suffixes:
            if folder_name.endswith(suffix) or course_name.endswith(suffix):
                return (
                    folder_name.replace(suffix, str(course_suffixes[suffix])) == course_name
                    or course_name.replace(suffix, str(course_suffixes[suffix])) == folder_name
                )
