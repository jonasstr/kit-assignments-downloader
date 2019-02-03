import logging
import os
from pathlib import Path
import re
import sys
import traceback

import click
from logging.handlers import RotatingFileHandler
from ruamel.yaml import YAML
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import tkinter as tk
from tkinter import filedialog

from kita import core
from kita.dao import Dao
from kita.assistant import Assistant
import kita.misc.utils as utils

gecko_path = os.path.join(Path(__file__).resolve().parents[1], "geckodriver")
user_yml_path = os.path.join(click.get_app_dir("kita"), "user.yml")
config_yml_path = os.path.join(Path(__file__).parents[0], "config.yml")

yaml = YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.compact(seq_seq=False, seq_map=False)

# Create data access object and load data on startup.
dao = Dao(gecko_path, user_yml_path, config_yml_path, yaml)
dao.load_data(suppress_access_errors=True)


def get_options():
    """Creates Firefox options for running kita in headless mode."""
    options = Options()
    options.headless = True
    return options


def is_positive_int(value):
    """

    :param value: 

    """
    return re.search("^\d+$", value)


def is_range(value):
    """

    :param value: 

    """
    return re.search("^\d+-\d+$", value)


def is_sequence(value):
    """

    :param value: 

    """
    return re.search("^\d+(?:,\d+)*$", value)


def print_info(ctx, param, value):

    if not value or ctx.resilient_parsing:
        return

    click.echo("Current user: {}".format(dao.user_data["user_name"]))
    click.echo("Root path: {}\n".format(dao.user_data["destination"]["root_path"]))
    added_courses = dao.added_courses()
    click.echo("Added courses:")
    for course in added_courses:
        click.echo("{}: {}".format(course.upper(), utils.reformat(dao.config_data[course]["path"])))
    available_courses = ", ".join(course.upper() for course in dao.config_data if course not in added_courses)
    click.echo("\nAvailable courses: {}".format(available_courses))
    ctx.exit()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(message="%(prog)s version %(version)s")
@click.option(
    "--info",
    "-i",
    is_flag=True,
    callback=print_info,
    expose_value=False,
    help="Show information about the current user and courses and exit.",
)
@click.pass_context
def cli(ctx):
    """Thank you for using the KIT Assignments Downloader!
    
    In order to download assignments make sure the setup was successful
    (otherwise run 'kita setup' again).\n
    To get started, just use the 'kita update la' command
    where 'la' is one of your courses.\n
    If you only want to download a specific assignment, use
    'kita get la 9' where '9' is the assignment number.\n   
    In case the download isn't working or you encounter any
    bugs/crashes please visit github.com/jonasstr/kita and
    create an issue or contact me via email: uzxhf@student.kit.edu.
    """
    if str(ctx.invoked_subcommand) is not "setup":
        # Make sure user.py has been created and config.yml exists.
        if setup_incorrectly("user.yml", user_yml_path) or setup_incorrectly("config.yml", config_yml_path):
            sys.exit(1)


def setup_incorrectly(file_name, path):
    if not os.path.isfile(path):
        click.echo(
            "\nKita has not been configured correctly ({} not found)."
            "\nUse 'kita setup' before downloading assignments.".format(file_name)
        )
        return True


@cli.command()
@click.option("--config", "-cf", is_flag=True, help="Change the download locations for the courses.")
@click.option("--user", "-u", is_flag=True, help="Change the current user and the root path for downloads.")
def setup(config, user):
    """Start the command line based setup assistant or change previous settings."""

    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)
    assistant = Assistant(yaml, dao)
    # Setup user.yml if either the --user option has been provided or no options at all.
    if user or user == config:
        if not assistant.setup_user():
            click.echo("Setup cancelled.")
            return
    # Setup config.yml if either the --config option has been provided or no options at all.
    if config or user == config:
        if not assistant.setup_config():
            click.echo("Setup cancelled.")
            return
    click.echo("\nSetup successful. Type 'kita --help' for details.")


def add(config):
    """Add a new course to the list of supported courses."""


def create_profile():
    """Create a Firefox profile required for navigating on a webpage.
    
    Set the preferences allowing PDFs to be downloaded immediately as well as
    navigating between tabs using keyboard shortcuts.

    :returns: The Firefox profile.
    """
    profile = webdriver.FirefoxProfile()
    # Set download location
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", dao.user_data["destination"]["root_path"])
    # Close download window immediately
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    # Download PDF files without asking the user
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    # Don't switch between recently visited tabs
    profile.set_preference("browser.ctrlTab.recentlyUsedOrder", False)
    # Move directly to newly opened tab
    profile.set_preference("browser.tabs.loadInBackground", False)
    return profile


def create_scraper(headless, verbose):
    driver = webdriver.Firefox(
        firefox_profile=create_profile(),
        executable_path=gecko_path,
        options=get_options() if headless else None,
    )
    return core.Scraper(driver, dao, verbose)


@cli.command()
@click.argument("course_names", nargs=-1, required=True, type=click.Choice(dao.config_data))
@click.argument("assignment_num")
@click.option(
    "--move/--keep",
    "-mv/-kp",
    default=True,
    help="Move the downloaded assignments to their course directory"
    " (same as 'kita update') or keep them in the browser's download directory (default: move).",
)
@click.option("--all", "-a", is_flag=True, help="Download assignments from all specified courses.")
@click.option(
    "--headless/--show", "-hl/-s", default=True, help="Start the browser in headless mode (no visible UI)."
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Print additional information during the download process."
)
def get(course_names, assignment_num, move, all, headless, verbose):
    """Download one or more assignments from the specified course(s) and move them into the correct folders."""

    if is_positive_int(assignment_num):
        assignments = [assignment_num]
    # Alternative range for assignment_num instead of int. Example: 5-10
    elif is_range(assignment_num):
        assignment_nums = assignment_num.split("-")
        assignments = range(int(assignment_nums[0]), int(assignment_nums[1]) + 1)
    # Alternative int sequence for assignment_num instead of int. Example: 5,10,11
    elif is_sequence(assignment_num):
        assignments = assignment_num.split(",")
    else:
        print("Assignment number must be an integer or in the correct format!")
        return

    scraper = create_scraper(headless, verbose)
    courses_to_iterate = dao.config_data if all else course_names

    for name in courses_to_iterate:
        course_ = dao.config_data[name]
        for num in assignments:
            scraper.get(course_, num, move)
    scraper.driver.quit()


@cli.command()
@click.argument("course_names", nargs=-1, required=False, type=click.Choice(dao.config_data))
@click.option("--all", "-a", is_flag=True, help="Update assignment directories for all specified courses.")
@click.option(
    "--headless/--show", "-hl/-s", default=True, help="Start the browser in headless mode (no visible UI)."
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Print additional information during the download process."
)
def update(course_names, all, headless, verbose):
    """Update one or more courses by downloading the latest assignments."""

    scraper = create_scraper(headless, verbose)
    all = True if not course_names else all
    courses_to_iterate = dao.config_data if all else course_names

    for name in courses_to_iterate:
        course_ = dao.config_data[name]
        scraper.update_directory(course_, name)
    scraper.driver.quit()


if __name__ == "__main__":
    cli()
