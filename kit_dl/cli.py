import os
from pathlib import Path
import re
import sys

import click
from ruamel.yaml import YAML
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import tkinter as tk

from kit_dl import core
from kit_dl.assistant import Assistant
from kit_dl.dao import Dao
import kit_dl.misc.utils as utils

gecko_path = os.path.join(Path(__file__).resolve().parents[1], "geckodriver.exe")
user_yml_path = os.path.join(click.get_app_dir("kit_dl"), "user.yml")
config_yml_path = os.path.join(Path(__file__).parents[0], "config.yml")

yaml = YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.compact(seq_seq=False, seq_map=False)

# Create data access object and load data on startup.
dao = Dao(gecko_path, user_yml_path, config_yml_path, yaml)


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
    (otherwise run 'kit-dl setup' again).\n
    To get started, just use the 'kit-dl update la' command
    where 'la' is one of your courses.\n
    If you only want to download a specific assignment, use
    'kit-dl get la 9' where '9' is the assignment number.\n
    In case the download isn't working or you encounter any
    bugs/crashes please visit github.com/jonasstr/kit-dl and
    create an issue or contact me via email: uzxhf@student.kit.edu.
    """
    if str(ctx.invoked_subcommand) != "setup" or not "show":
        # Make sure user.py has been created and config.yml exists.
        if setup_incorrectly("user.yml", user_yml_path) or setup_incorrectly("config.yml", config_yml_path):
            sys.exit(1)
        else:
            dao.load_data(suppress_access_errors=True)


def setup_incorrectly(file_name, path):
    if not os.path.isfile(path):
        click.echo(
            "\nKit-dl has not been configured correctly ({} not found)."
            "\nUse 'kit-dl setup' before downloading assignments.".format(file_name)
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
    click.echo("\nSetup successful. Type 'kit-dl --help' for details.")


@cli.command()
@click.argument("course_names", nargs=-1, required=True, type=click.Choice(dao.config_data))
@click.argument("assignment_num")
@click.option(
    "--move/--keep",
    "-mv/-kp",
    default=True,
    help="Move the downloaded assignments to their course directory"
    " (same as 'kit-dl update') or keep them in the browser's download directory (default: move).",
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
    assignments = get_assignments(assignment_num)
    if assignments is None:
        print("Assignment number must be an integer or in the correct format!")
        return

    scraper = create_scraper(headless, verbose)
    try:
        for name in courses_to_iterate(course_names, all):
            course = dao.config_data[name]
            for num in assignments:
                scraper.get(course, num, move)
    finally:
        scraper.driver.quit()


def get_assignments(input):
    assignments = None
    if is_positive_int(input):
        assignments = [input]
    # Alternative range for assignment nums instead of int. Example: 5-10
    elif is_range(input):
        assignment_nums = input.split("-")
        assignments = range(int(assignment_nums[0]), int(assignment_nums[1]) + 1)
    # Alternative int sequence for input instead of int. Example: 5,10,11
    elif is_sequence(input):
        assignments = input.split(",")
    return assignments


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
    try:
        for name in courses_to_iterate(course_names, all):
            course = dao.config_data[name]
            scraper.update_directory(course, name)
    finally:
        scraper.driver.close()


def courses_to_iterate(course_names, all):
    if not course_names:
        all = True
    return dao.config_data if all else course_names


def create_scraper(headless, verbose):
    driver = webdriver.Firefox(
        firefox_profile=create_profile(),
        executable_path=gecko_path,
        options=get_options() if headless else None,
    )
    return core.Scraper(driver, dao, verbose)


def get_options():
    """Creates Firefox options for running kit-dl in headless mode."""
    options = Options()
    options.headless = True
    return options


def is_positive_int(value):
    return re.search(r"^\d+$", value)


def is_range(value):
    return re.search(r"^\d+-\d+$", value)


def is_sequence(value):
    return re.search(r"^\d+(?:,\d+)*$", value)


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


@cli.command()
@click.password_option()
def show(password):
    click.echo("PW=" + password)


if __name__ == "__main__":
    cli()
