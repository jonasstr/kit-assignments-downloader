import os
import tkinter as tk
from tkinter import filedialog

from colorama import Fore, Style
from colorama import init
import click

from kita.misc.logger import Logger
import kita.misc.utils as utils

class Assistant:

    def __init__(self, yaml, dao):
        # Initialize colorama.
        init()
        self.yaml = yaml
        self.dao = dao    
        root = tk.Tk() 
        root.withdraw()
        root.wm_attributes("-topmost", True)


    def echo(self, text, is_prompt=False):
        """Forwards the given text to click.echo() and optionally applies a different style to the text.
    
        :param text: The text to print to the standard output.
        :type text: str
        :param is_prompt: Whether the text should be viewed as a user prompt.
            If true, adds cyan color and a '>' symbol to the start of the string to be distinct from default output.
    
        """
        color = Fore.CYAN if is_prompt else Style.RESET_ALL
        if is_prompt:
            text = "> " + text
        click.echo(color + text)


    def prompt(self, text):
        """Forwards the given text to click.echo() and adds cyan color and a '>' symbol to the start of the string.
    
        :param text: The text to print to the standard output.
        :type text: str
    
        """
        return click.prompt(Fore.CYAN + "> " + text)


    def confirm(self, text, default=False):
        """
    
        :param text: 
        :param default:  (Default value = False)
    
        """
        suffix = " (Y/n) [y]: " if default else " (y/N) [n]: "
        return click.confirm(Fore.CYAN + "> " + text, default=default, show_default=False, prompt_suffix=suffix)
    
    
    def show_kit_folder_detected_dialog(self, assignment_folders, root_path):    
        """Asks the user to confirm the download locations for the given courses.
    
        :param assignment_folders: The detected assignment folders.
        :type assignment_folders: dict
        :param root_path: The absolute path to the user's assignment download location.
        :type root_path: str
        """
    
        self.echo("\nPossible KIT folder detected:")
        for folder in assignment_folders:
            course_key = folder[0]
            detected_path = folder[1]
            full_path = os.path.join(root_path, detected_path)
            message = utils.reformat("Save {} assignments to '{}' folder?".format(course_key.upper(), full_path))
            if self.confirm(message, default=True):
                self.dao.config_data[course_key]['path'] = detected_path
                self.dao.dump_config()
        self.show_confirm_all_courses_dialog()
        

    def show_confirm_all_courses_dialog(self):
        added_courses = self.dao.added_courses()
        if not added_courses:
            self.show_create_course_folder_dialog(assignment_folders, root_path)
            return
        self.update_selected_courses(added_courses)
        while self.choice and not self.confirm("Are these all courses: {}?".format(self.selected), default=True):
            selection = self.show_select_folder_manually_dialog(self.choice)
            self.show_assignments_save_location_dialog(selection)
            added_courses.append(selection['course_key'].lower())
            self.update_selected_courses(added_courses)


    def update_selected_courses(self, added_courses):
        self.selected = ', '.join(course.upper() for course in added_courses)
        self.choice = ', '.join(key.upper() for key in self.dao.config_data.keys() if key not in added_courses)


    def show_assignments_save_location_dialog(self):
        self.echo("{} assignments will be saved to '{}'.".format(
            selection['course_key'].upper(), utils.reformat(selection['selected_path'])))
        self.dao.config_data[selection['course_key']]['path'] = selection['selected_path']
        self.dao.dump_config()


    def show_create_course_folder_dialog(self, assignment_folders, root_path):
        """
    
        :param assignment_folders: 
        :param root_path: 
        """
        download_dir = os.path.join(root_path, "Downloads")
        os.makedirs(download_dir, exist_ok=True)
        
        for folder in assignment_folders:
            course_key = folder[0]
            if course_key in dao.config:
                course_name = self.dao.config_data[course_key]['name'].replace('/','-').replace('\\','-')
                course_dir = os.path.join(download_dir, course_name)
                os.makedirs(course_dir, exist_ok=True)
                dao.config_data['courses'][course_key]['path'] = course_dir
                self.dao.dump_config()
        self.echo("Downloads will be saved to '{}'.".format(utils.reformat(download_dir)))


    def show_select_folder_manually_dialog(self, choice):
        """Prints the setup dialog for adding the location of additional assignments.
    
        :param choice: The set of the possible courses to choose from.
        :returns: The name of the selected course and the path chosen from the folder selection dialog window.
        :rtype: tuple
        """
        course_name = self.prompt("Which courses are missing? Choose from {}".format(choice))
        while not course_name.lower() in self.dao.config_data.keys():
            self.echo("Error: invalid input")
            course_name = self.prompt("Which courses are missing? Choose from {}".format(choice))
        self.echo("Choose a location for saving your {} courses:".format(course_name.upper()), is_prompt=True)
        return {'course_key' : course_name, 'selected_path' : filedialog.askdirectory()}

    
    def setup_config(self):
        """Starts the setup assistant for setting up the config.yml file."""
        if os.path.isfile(self.dao.user_yml_path):
            self.dao.load_user()

            root_path = self.dao.user_data['destination']['root_path']
            if not os.path.isdir(root_path):
                self.echo("\nKita has not been configured correctly (root_path not found).\nUse 'kita setup --user' instead.")
                return False
    
            assignment_folders = self.detected_assignment_folders(root_path)
            if assignment_folders:
                self.show_kit_folder_detected_dialog(assignment_folders, root_path)
            return True
        else: return False


    def detected_assignment_folders(self, root_path):
        sub_folders = next(os.walk(root_path))[1]            
        assignment_folders = []
        for folder_name in sub_folders:
            folder_path = os.path.join(root_path, folder_name)
            result = self.search_for_assignments_folder(folder_path, folder_name)
            if result:
                assignment_folders.append(result)
        return assignment_folders


    def search_for_assignments_folder(self, folder_path, folder_name):
        """Searches for a possible folder containing the assignments based on the folder name."""
        for course_key in self.dao.config_data:
            # Folder has been found.
            print(str(course_key))
            if course_key == folder_name.lower() or self.are_similar(folder_name, self.dao.config_data[course_key]['name']):
                sub_folders = next(os.walk(folder_path))[1]
                sub_folder_name = self.found_assignments_sub_folder(folder_name, sub_folders)
                return (course_key, sub_folder_name) if sub_folder_name else (course_key, folder_name)


    def found_assignments_sub_folder(self, folder_name, sub_folders):
        for sub_folder in sub_folders:
            name_list = ['übungsblätter', 'blätter', 'assignments']
            # Check whether the name of the sub-folder is either one of the above names.
            if any(x in sub_folder.lower() for x in name_list):
                return os.path.join(folder_name, sub_folder)


    def are_similar(self, folder_name, course_name):
        """Checks whether a given folder name is similar to the full name of a config.yml course
                or is equal to the course key (e.g. la).
        
        "Similar" in this case only refers to the ending of the folder name.
        
        :param folder_name: The name of the folder to check.
        :type folder_name: str
        :param course_name: The course key or full name to compare the folder name to.
        :type course_name: str
        :returns: Whether the folder_name is included in the course_name or vice versa, or whether
            the only differnce between the strings are the file endings (roman instead of latin digits).
        """
        if folder_name.startswith(course_name) or course_name.startswith(folder_name):
            return True
        course_suffixes = {'I': 1, 'II': 2, 'III': 3}
        for suffix in course_suffixes:
            if folder_name.endswith(suffix):
                # Check if the folder name is equivalent to the course name apart from the roman suffix.
                return folder_name.replace(suffix, str(course_suffixes[suffix])) == course_name
    
        
    
    def setup_user(self):
        """Starts the setup assistant for setting up the user.yml file.
    
        Saves the login credentials of the user and the root path for downloading assignments.
        """
        # user.yml already exists.
        if os.path.isfile(self.dao.user_yml_path):
            if not self.confirm("Kita is already set up. Overwrite existing config?"):
                return False
    
        self.echo("\nWelcome to the Kita 1.0.0 setup utility.\n\nPlease enter values for the following "
            "settings (just press Enter to\naccept a default value, if one is given in brackets).\n")
    
        data = {}
        data['user_name'] = self.prompt("Enter your correct ilias user name").strip()
        data['password'] = self.prompt("Enter your ilias password").strip()
        self.echo("\nChoose a location for saving your assignments. If you already\n"
            "downloaded assignments manually please choose your KIT folder\nfor auto-detection.")
        self.echo("Select the root path for your assignments from the dialog window:", is_prompt=True)
        
        root_path = os.path.abspath(filedialog.askdirectory())
        data['destination'] = {}
        data['destination']['root_path'] = root_path
        # Set default rename format.
        data['destination']['rename_format'] = "Blatt$$"
        self.dao.create_user(data)

        self.echo("Downloads will be saved to '{}'.".format(utils.reformat(root_path)))
        return True 