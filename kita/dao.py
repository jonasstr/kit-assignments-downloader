import os
from pathlib import Path

import click
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


class UnsafeCommentedMap(CommentedMap):        

        def __getitem__(self, key):
            if key in self:
                return CommentedMap.__getitem__(self, key)
            else: click.echo("Key {} not found!".format(key))

class Dao:

    def __init__(self, gecko_path, user_yml_path, config_yml_path):
        self.gecko_path = os.path.join(Path(__file__).parents[0], "geckodriver.exe")
        self.user_yml_path = os.path.join(click.get_app_dir("kita"), "user.yml")
        self.config_yml_path = os.path.join(Path(__file__).parents[0], "config.yml")
        self.user_data = None
        self.root_path = None
        self.all_courses = None
        self.yaml = YAML(typ='rt')
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.compact(seq_seq=False, seq_map=False)


    def try_load_file(self, path, error_msg):
        """Tries to load the specified yaml file.
        If the path is incorrect, reraises the exception and prints the specified error messsage.
    
        :param path: The absolute of the yaml file to load.
        :type path: str
        :param error_msg: The error message to print in case the file could not be loaded.
        :returns: The content of the file using yaml.load()
        :rtype: dict
        """
        try:
            with open(path, 'rb') as file:
                return self.yaml.load(file)
        except Exception as e:
            raise
            click.echo(error_msg)
    
    
    def load_data(self, suppress_access_errors=False):
        """Loads the user.yml and config.yml files."""
        self.user_data = self.try_load_file(self.user_yml_path,
            error_msg = "Error, cannot find user.yml. \n"
                    "Use 'kita setup' before downloading assignments.")
        self.all_courses = self.try_load_file(self.config_yml_path,
            error_msg = "Error, cannot find config.yml.")['courses']

        # Caution! Only use when program logic does not depend on possible null state of attributes! (e.g. for logging)
        # May be hard to find sources for unexpected behaviour or can hide bugs!
        if suppress_access_errors:
            self.user_data = UnsafeCommentedMap(self.user_data)
            self.all_courses = UnsafeCommentedMap(self.all_courses)


    def added_courses(self):
        result = []
        for course in self.all_courses:
            path = self.all_courses[course]['path']
            if path:
                result.append(course)
        return result
