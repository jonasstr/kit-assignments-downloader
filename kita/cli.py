import logging
import os
from pathlib import Path
import re
import sys
import tkinter as tk
from tkinter import filedialog
import traceback

from colorama import Fore, Style
from colorama import init
import click
from logging.handlers import RotatingFileHandler
from ruamel.yaml import YAML
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from kita import core
from kita.misc.logger import Logger
import kita.misc.utils as utils

# Initialize colorama.
init()
yaml = YAML(typ='rt')
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.compact(seq_seq=False, seq_map=False)

gecko_path = os.path.join(Path(__file__).parents[1], "geckodriver.exe")
user_yml_path = os.path.join(click.get_app_dir("kita"), "user.yml")
config_yml_path = os.path.join(Path(__file__).parents[0], "config.yml")
user_data = None
root_path = None
all_courses = None

def try_load_file(path, error_msg):
	try:
		with open(path, 'rb') as file:
			return yaml.load(file)
	except Exception as e:
		raise
		click.echo(error_msg)

def load_data():
	global user_data
	user_data = try_load_file(user_yml_path,
		error_msg = "Error, cannot find user.yml. \n"
				"Use 'kita setup' before downloading assignments.")
	global root_path
	root_path = user_data['destination']['root_path']
	global all_courses
	all_courses = try_load_file(config_yml_path,
		error_msg = "Error, cannot find config.yml.")['courses']

# Load data on startup.
load_data()

def get_options():
	'''
	Returns: 
		The options for running Firefox in headless mode.
	'''
	options = Options()
	options.headless = True
	return options

def create_profile():
	"""Creates a Firefox profile required for navigating on a webpage.
	Sets the preferences allowing PDFs to be downloaded immediately as well as
	navigating between tabs using keyboard shortcuts.
	
	Returns:
		The Firefox profile.
	"""
	profile = webdriver.FirefoxProfile()
	# Set download location
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.dir", user_data['destination']['root_path'])

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

def is_positive_int(value):
	return re.search('^\d+$', value)

def is_range(value):
	return re.search('^\d+-\d+$', value)

def is_sequence(value):
	return re.search('^\d+(?:,\d+)*$', value)

def echo(text, is_prompt=False):
	color = Fore.CYAN if is_prompt else Style.RESET_ALL
	if is_prompt:
		text = "> " + text
	click.echo(color + text)

def prompt(text):
	return click.prompt(Fore.CYAN + "> " + text)

def confirm(text, default=False):
	suffix = " (Y/n) [y]: " if default else " (y/N) [n]: "
	return click.confirm(Fore.CYAN + "> " + text, default=default, show_default=False, prompt_suffix = suffix)

@click.version_option()
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
def cli(ctx):
	load_data()
	'''Thank you for using the KIT Assignments Downloader!

	In order to download assignments make sure the setup was successful 
	(run 'kita setup' again if not).

	To get started, just use the 'kita update la' command
	where 'la' is one of your courses.

	If you only want to download a specific assignment, use
	'kita get la 9' where '9' is the assignment number.

	In case the download isn't working or you encounter any
	bugs/crashes please visit github.com/jonasstr/kita and
	create an issue or contact me via email: uzxhf@student.kit.edu.
	'''
	if ctx.invoked_subcommand is not 'setup':
		print(ctx.invoked_subcommand)


@cli.command()
@click.argument('type', required=True, type=click.Choice(['config', 'user']))
def view(type):
	if type == 'config':
		print("open cfg")
	elif type == 'user':
		print("open user")


def is_similar(folder_name, course_name):
	'''Checks whether a given folder name is similar to the full name of a config.yml course
		or is equal to the course key (e.g. la).

	"Similar" in this case only refers to the ending of the folder name.

	Args:
		folder_name (str): The name of the folder to check.
		course_name (str): The course key or full name to compare the folder name to.

	Returns:
		Whether the folder_name is included in the course_name or vice versa, or whether
		the only differnce between the strings are the file endings (roman instead of latin digits).

	'''
	if (folder_name.startswith(course_name) or course_name.startswith(folder_name)):
		return True
	course_suffixes = {'I': 1, 'II': 2, 'III': 3}
	for suffix in course_suffixes:
		if folder_name.endswith(suffix):
			# Check if the folder name is equivalent to the course name apart from the roman suffix.
			return folder_name.replace(suffix, str(course_suffixes[suffix])) == course_name

def find_assignments_folder(folder_path, folder_name):
	'''Searches for a possible folder containing the assignments based on the folder name.

	Args:
		folder_path (str): The absolute path of the assignment folder to search in.
		folder_name (str): The name of the folder.

	Returns:
		tuple: The course key and the absolute path of the found folder, None if no assignment folder was found. 

	'''
	for course_ in all_courses:
		# Folder has been found.
		if folder_name.lower() == course_ or is_similar(folder_name, all_courses[course_]['name']):
			sub_folders = next(os.walk(folder_path))[1]
			# Search for possible assignment sub-folders.
			for sub_folder in sub_folders:
				name_list = ['übungsblätter', 'blätter', 'assignments']
				# Check whether the name of the sub-folder is either one of the above names.
				if any(x in sub_folder.lower() for x in name_list):
					return (course_, os.path.join(folder_name, sub_folder))
			return (course_, folder_name)
	return None

def show_select_folder_manually_dialog(choice):
	'''Prints the setup dialog for adding the location of additional assignments.

	Args:
		choice: The set of the possible courses to choose from.

	Returns:
		tuple: The name of the selected course and the path chosen from the folder selection dialog window.

	'''
	course_name = prompt("Which courses are missing? Choose from {}".format(choice))
	while not course_name.lower() in all_courses.keys():
		echo("Error: invalid input")
		course_name = prompt("Which courses are missing? Choose from {}".format(choice))
	echo("Choose a location for saving your {} courses:".format(course_name.upper()), is_prompt=True)
	return (course_name, filedialog.askdirectory())

def show_create_course_folders_dialog(assignment_folders, root_path):
	'''
	'''
	download_dir = os.path.join(root_path, "Downloads")
	os.makedirs(download_dir, exist_ok=True)
	with open(config_yml_path, 'rb') as cfg_path:
		config = yaml.load(cfg_path)
	for folder in assignment_folders:
		course_key = folder[0]
		if course_key in all_courses:
			course_name = config['courses'][course_key]['name'].replace('/','-').replace('\\','-')
			course_dir = os.path.join(download_dir, course_name)
			os.makedirs(course_dir, exist_ok=True)
			config['courses'][course_key]['path'] = course_dir
	with open(config_yml_path, 'w', encoding='utf-8') as cfg_path:
		yaml.dump(config, cfg_path)
	echo("Downloads will be saved to '{}'.".format(utils.reformat(download_dir)))

def dump_course_path(course_key, course_path):
	# Open config.yml in read binary mode.
	config = yaml.load(open(config_yml_path, 'rb'))
	config['courses'][course_key]['path'] = course_path
	with open(config_yml_path, 'w', encoding='utf-8') as cfg_path:
		yaml.dump(config, cfg_path)


def show_kit_folder_detected_dialog(assignment_folders, root_path):	

	echo("\nPossible KIT folder detected:")
	added_courses = []
	for folder in assignment_folders:
		course_key = folder[0]
		detected_path = folder[1]
		message = utils.reformat("Save {} assignments to '{}' folder?".format(course_key.upper(), detected_path))
		if confirm(message, default=True):
			added_courses.append(course_key)
			dump_course_path(course_key, detected_path)

	if not added_courses:
		show_create_course_folders_dialog(assignment_folders, root_path)
		return

	selected = ', '.join(course_.upper() for course_ in added_courses)
	choice = ', '.join(key.upper() for key in all_courses.keys() if key not in added_courses)
	while choice and not confirm("Are these all courses: {}?".format(selected), default=True):
		selection = show_select_folder_manually_dialog(choice)
		added_courses.append(selection[0].lower())
		selected = ', '.join(course_.upper() for course_ in added_courses)
		choice = ', '.join(key for key in all_courses.keys() if key not in added_courses)

		selected_path = selection[1]
		if selected_path:
			echo("{} assignments will be saved to '{}'.".format(course_key.upper(), utils.reformat(selected_path)))
			dump_course_path(course_key, selected_path)

def setup_config():
	# Make sure user.yml has been set up.
	if os.path.isfile(user_yml_path):
		# Open user.yml in read binary mode.
		with open(user_yml_path, 'rb') as cfg:
			file_size = os.path.getsize(user_yml_path)
			if file_size > 0:
				user_data = yaml.load(cfg)
			if file_size > 0 and 'destination' in user_data and 'root_path' in user_data['destination']:
				root_path = user_data['destination']['root_path']
			else: 
				echo("\nKita has not been configured correctly (empty config file).\nUse 'kita setup --user' instead.")
				return False

		if not os.path.isdir(root_path):
			echo("\nKita has not been configured correctly (root_path not found).\nUse 'kita setup --user' instead.")
			return False

		sub_folders = next(os.walk(root_path))[1]			
		assignment_folders = []
		for folder in sub_folders:
			folder_path = os.path.join(root_path, folder)
			result = find_assignments_folder(folder_path, folder)
			if result:
				assignment_folders.append(result)
	
		if assignment_folders:
			show_kit_folder_detected_dialog(assignment_folders, root_path)
		return True
	else: return False

def setup_user():
	# user.yml already exists.
	if os.path.isfile(user_yml_path):
		if not confirm("Kita is already set up. Overwrite existing config?"):
			return False

	echo("\nWelcome to the Kita 1.0.0 setup utility.\n\nPlease enter values for the following "
		"settings (just press Enter to\naccept a default value, if one is given in brackets).\n")

	data = {}
	data['user_name'] = prompt("Enter your correct ilias user name").strip()
	data['password'] = prompt("Enter your ilias password").strip()
	echo("\nChoose a location for saving your assignments. If you already\n"
		"downloaded assignments manually please choose your KIT folder\nfor auto-detection.")
	echo("Select the root path for your assignments from the dialog window:", is_prompt=True)
	
	root_path = os.path.abspath(filedialog.askdirectory())
	print("SLCTED PATH: " + root_path)
	data['destination'] = {}
	data['destination']['root_path'] = root_path
	# Set default rename format.
	data['destination']['rename_format'] = "Blatt$$"
	echo("Downloads will be saved to '{}'.".format(utils.reformat(root_path)))

	os.makedirs(os.path.dirname(user_yml_path), exist_ok=True)
	with open(user_yml_path, 'w', encoding='utf-8') as user_path:
		yaml.dump(data, user_path)
	return True

def disable_event():
	pass

@cli.command()
@click.option('--config', '-cf', is_flag=True, help="Change the download locations for the courses.")
@click.option('--user', '-u', is_flag=True, help="Change the current user and the root path for downloads.")
def setup(config, user):

	root = tk.Tk() 
	root.withdraw()
	root.wm_attributes("-topmost", True)

	# Setup user.yml if either the --user option has been provided or no options at all.
	if user or user == config:
		if not setup_user():
			echo("Setup cancelled.")
			return
	# Setup config.yml if either the --config option has been provided or no options at all.
	if config or user == config:
		if not setup_config():
			echo("Setup cancelled.")
			return
	echo("\nSetup successful. Type 'kita --help' for details.")	

@cli.command()
@click.argument('course_names', nargs=-1, required=True, type=click.Choice(all_courses))
@click.argument('assignment_num')
@click.option('--move', '-mv', is_flag=True, help="Move the downloaded assignments to the specified directory and rename them.")
@click.option('--all', '-a', is_flag=True, help="Download assignments from all specified courses.")
@click.option('--headless/--visible', '-hl/-v', default=True, help="Start the browser in headless mode (no visible UI).")
def get(course_names, assignment_num, move, all, headless):
	print("GET CALLED")

	if is_positive_int(assignment_num):
		assignments = [assignment_num]
	# Alternative range for assignment_num instead of int. Example: 5-10
	elif is_range(assignment_num):
		assignment_nums = assignment_num.split('-')
		assignments = range(int(assignment_nums[0]), int(assignment_nums[1]) + 1)
	# Alternative int sequence for assignment_num instead of int. Example: 5,10,11
	elif is_sequence(assignment_num):
		assignments = assignment_num.split(',')
	else: 
		print("Assignment number must be an integer or in the correct format!")
		return
	
	driver = webdriver.Firefox(firefox_profile=create_profile(),
		executable_path=gecko_path,
		options=get_options() if headless else None)

	scraper = core.Scraper(driver, user_data, root_path)
	courses_to_iterate = all_courses if all else course_names
	
	for name in courses_to_iterate:
		try:
			course_ = all_courses[name]
			for num in assignments:
				scraper.get(course_, num, move)
		except (IOError, OSError):
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
	print("Exiting")
	driver.quit()

@cli.command()
@click.argument('course_names', nargs=-1, required=False, type=click.Choice(all_courses))
@click.option('--all', '-a', is_flag=True, help="Update assignment directories for all specified courses.")
@click.option('--headless/--visible', '-hl/-v', default=True,  help="Start the browser in headless mode (no visible UI).")
def update(course_names, all, headless):
	driver = webdriver.Firefox(firefox_profile=create_profile(),
		executable_path=gecko_path,
		options=get_options() if headless else None)

	scraper = core.Scraper(driver, user_data, root_path)
	courses_to_iterate = all_courses if all else course_names
	
	for name in courses_to_iterate:
		try:
			course_ = all_courses[name]
			scraper.update_directory(course_, name)
		except (IOError, OSError):
			raise
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
	print("Exiting")
	driver.quit()	

if __name__ == '__main__':
	cli()