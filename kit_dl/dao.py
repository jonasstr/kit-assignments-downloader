import os

import click
from ruamel.yaml.comments import CommentedMap


class UnsafeCommentedMap(CommentedMap):
    def __getitem__(self, key):
        if key in self:
            return CommentedMap.__getitem__(self, key)
        else:
            click.echo("Key {} not found!".format(key))


class Dao:
    def __init__(self, gecko_path, user_yml_path, config_yml_path, yaml):
        self.gecko_path = gecko_path
        self.user_yml_path = user_yml_path
        self.config_yml_path = config_yml_path
        self.user_data = None
        self.root_path = None
        self.config_data = None
        self.yaml = yaml

    def try_load_file(self, path, error_msg=None):
        """Tries to load the specified yaml file.
        If the path is incorrect, reraises the exception and prints the specified error messsage.

        :param path: The absolute of the yaml file to load.
        :type path: str
        :param error_msg: The error message to print in case the file could not be loaded.
        :returns: The content of the file using yaml.load()
        :rtype: dict
        """
        try:
            with open(path, "rb") as file:
                return self.yaml.load(file)
        except Exception:
            if error_msg:
                click.echo(error_msg)

    def load_data(self, suppress_access_errors=False):
        """Loads the user.yml and config.yml files."""
        self.user_data = self.try_load_file(
            self.user_yml_path,
            error_msg="Error, cannot find user.yml. \n" "Use 'kit-dl setup' before downloading assignments.",
        )
        self.config_data = self.try_load_file(self.config_yml_path, error_msg="Error, cannot find config.yml.")

        # Caution! Only use when program logic does not depend on possible null state of attributes!
        # (e.g. for logging)
        # May be hard to find sources for unexpected behaviour or can hide bugs!
        if suppress_access_errors:
            self.user_data = UnsafeCommentedMap(self.user_data)
            self.config_data = UnsafeCommentedMap(self.config_data)

    def load_user(self):
        self.user_data = self.try_load_file(
            self.user_yml_path,
            error_msg="Error, cannot find user.yml. \n" "Use 'kit-dl setup' before downloading assignments.",
        )

    def load_config(self):
        self.config_data = self.try_load_file(self.config_yml_path, error_msg="Error, cannot find config.yml.")

    def create_user(self, data):
        os.makedirs(os.path.dirname(self.user_yml_path), exist_ok=True)
        with open(self.user_yml_path, "w", encoding="utf-8") as user_path:
            self.yaml.dump(data, user_path)

    def dump_config(self):
        """Dumps the specified course path into the config.yml file for a given course.

        :param course_key: The key of the course in the config.yml file e.g. la.
        :type course_key: str
        :param course_path: The absolute path of the course directory.
        :type course_path: str
        """
        # Open config.yml in read binary mode.
        with open(self.config_yml_path, "w", encoding="utf-8") as cfg_path:
            self.yaml.dump(CommentedMap(self.config_data), cfg_path)

    def added_courses(self):
        result = []
        for course in self.config_data:
            path = self.config_data[course]["path"]
            if path:
                result.append(course)
        return result
