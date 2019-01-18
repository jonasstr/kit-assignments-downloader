import logging
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog
import traceback

import click
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from logging.handlers import RotatingFileHandler
from ruamel.yaml import YAML

import core
from misc.logger import Logger
import misc.utils as utils


yaml = YAML(typ='rt')
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.compact(seq_seq=False, seq_map=False)

user_yml_path = os.path.join(click.get_app_dir("kita"), "user.yml")
cfg_yml_path = os.path.join(click.get_app_dir("kita"), "config.yml")

with open("user.yml", encoding='utf-8') as user:
	user_data = yaml.load(user)
	download_path = user_data['download_path']

with open("config.yml", encoding='utf-8') as config:
	config_data = yaml.load(config)
	all_classes = config_data['classes']

def get_options():
	options = Options()
	options.headless = True
	return options

def create_profile():
	"""
	Sets the Firefox preferences
	"""
	profile = webdriver.FirefoxProfile()
	# Download to specified path
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", download_path)
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

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def main():
	'''Test
	'''
	print("MAIN")

@main.command()
@click.argument('type', required=True, type=click.Choice(['config', 'user']))
def view(type):
	if type == 'config':
		print("open cfg")
	elif type == 'user':
		print("open user")


def is_similar(folder_name, class_):
	class_name = class_['name']
	if (folder_name.startswith(class_name) or class_name.startswith(folder_name)):
		return True
	class_suffixes = {'I': 1, 'II': 2, 'III': 3}
	for suffix in class_suffixes:
		if folder_name.endswith(suffix):
			return folder_name.replace(suffix, str(class_suffixes[suffix])) == class_name

def find_assignments_folder(path, folder_name):
	for name in all_classes:
		# Folder has been found.
		if folder_name.lower() == name or is_similar(folder_name, all_classes[name]):
			sub_folders = next(os.walk(path))[1]
			# Search for possible assignment sub-folders.
			for sub_folder in sub_folders:
				name_list = ['übungsblätter', 'blätter', 'assignments']
				if any(x in sub_folder.lower() for x in name_list):
					return (name, os.path.join(folder_name, sub_folder))
			return (name, folder_name)
	return None

def select_folder_manually(choice):

	class_ = click.prompt("Which classes are missing? Choose from {}".format(choice))
	while not class_.lower() in all_classes.keys():
		click.echo("Error: invalid input")
		class_ = click.prompt("Which classes are missing? Choose from {}".format(choice))
	click.echo("Choose a location for saving your {} classes".format(class_.upper()))
	return (class_, filedialog.askdirectory())


@main.command()
@click.option('--config', '-cf', is_flag=True, help="Setup the classes (config.yml) file")
@click.option('--user', '-u', is_flag=True, help="Setup the user.yml file")
def setup(config, user):
	print(user_yml_path)
	# Setup config.yml if either the --config option has been provided or no options at all.
	setup_config = config or config == user
	# Setup user.yml if either the --user option has been provided or no options at all.
	setup_user = user or user == config
	if setup_user:
		# user.yml already exists.
		if os.path.isfile(user_yml_path):
			if not click.confirm("Kita is already set up. Overwrite existing config?"):
				click.echo("\nSetup cancelled.")
				return

		data = {}
		data['user_name'] = click.prompt("Please enter your correct ilias user name").strip()
		data['password'] = click.prompt("Please enter your ilias password").strip()
		click.echo("Choose a location for saving your assignments")

		root = tk.Tk()
		root.withdraw()
		selected_path = filedialog.askdirectory()

		data['destination'] = {}
		data['destination']['root_path'] = selected_path
		click.echo("Downloads will be saved to '{}'.".format(selected_path))

		os.makedirs(os.path.dirname(user_yml_path), exist_ok=True)
		with open(user_yml_path, 'w') as user_path:
			yaml.dump(data, user_path)

	if setup_config:
		# Make sure user.yml has been set up.
		if os.path.isfile(user_yml_path):
			with open(user_yml_path, 'w') as cfg:
				if os.path.getsize(user_yml_path) > 0:
					user_data = yaml.load(cfg)
				# TODO: fix
				if user_data is not None and 'destination' in user_data and 'root_path' in user_data['destination']:
					root_path = user_data['destination']['root_path']
				else: 
					click.echo("Kita has not been configured correctly. Use 'kita setup --user' instead."
						"\nSetup cancelled.")
					return

			sub_folders = next(os.walk(root_path))[1]			
			assignment_folders = []
			for folder in sub_folders:
				path = os.path.join(root_path, folder)
				result = find_assignments_folder(path, folder)
				if result:
					assignment_folders.append(result)
		
			if assignment_folders:
				click.echo("\nPossible KIT folder detected:")
				added_classes = []
				for folder in assignment_folders:
					message = utils.reformat("Save {} assignments to '{}' folder?".format(folder[0].upper(), folder[1]))
					if click.confirm(message, default=True):
						added_classes.append(folder[0])
					click.echo('OK')
		
				selected = ', '.join(class_.upper() for class_ in added_classes)
				choice = ', '.join(key.upper() for key in all_classes.keys() if key not in added_classes)
				while choice and not click.confirm("Are these all classes: {}?".format(selected)):
					selection = select_folder_manually(choice)
					class_key = selection[0].lower()
					path = selection[1]
					added_classes.append(class_key)
					choice = ', '.join(key for key in all_classes.keys() if key not in added_classes)
		
					if path:
						config = yaml.load(open('config.yml'))
						class_ = config['classes'][class_key]
						class_['path'] = path
		
						print("Add {} path {}.".format(class_key, path))
						with open('config.yml', 'w', encoding='utf-8') as cfg_path:
							yaml.dump(config, cfg_path)

	click.echo("\nSetup successful. Type 'kita --help' for details.")



@main.command()
@click.argument('class_names', nargs=-1, required=True, type=click.Choice(all_classes))
@click.argument('assignment_num')
@click.option('--move', '-mv', is_flag=True, help="Move the downloaded assignments to the specified directory and rename them.")
@click.option('--all', '-a', is_flag=True, help="Download assignments from all specified classes.")
@click.option('--headless/--visible', '-hl/-v', default=True, help="Start the browser in headless mode (no visible UI).")
def get(class_names, assignment_num, move, all, headless):
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
	
	driver = webdriver.Firefox(firefox_profile=create_profile(), options=get_options() if headless else None)

	scraper = kita.Scraper(driver, user_data)
	classes_to_iterate = all_classes if all else class_names
	
	for name in classes_to_iterate:
		try:
			class_ = all_classes[name]
			for num in assignments:
				scraper.get(class_, num, move)
		except (IOError, OSError):
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
	print("Exiting")
	driver.quit()

@main.command()
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(all_classes))
@click.option('--all', '-a', is_flag=True, help="Update assignment directories for all specified classes.")
@click.option('--headless/--visible', '-hl/-v', default=True,  help="Start the browser in headless mode (no visible UI).")
def update(class_names, all, headless):
	print("UPDATE")
	driver = webdriver.Firefox(firefox_profile=create_profile(), options=get_options() if headless else None)

	scraper = kita.Scraper(driver, user_data)
	classes_to_iterate = all_classes if all else class_names
	
	for name in classes_to_iterate:
		try:
			class_ = all_classes[name]
			scraper.update_directory(class_)
		except (IOError, OSError):
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
	print("Exiting")
	driver.quit()

if __name__ == '__main__':
	main()
