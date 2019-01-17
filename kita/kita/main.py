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
from logger import Logger
from logging.handlers import RotatingFileHandler
import ruamel.yaml as yaml

import kita
import utils


yaml = yaml.YAML(typ='safe')
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
	

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def main():
	'''Test
	'''
	print("MAIN")

def select_folder_manually(choice):

	class_ = click.prompt("Which classes are missing? Choose from {}".format(choice))
	while not class_ in all_classes.keys():
		click.echo("Error: invalid input")
		class_ = click.prompt("Which classes are missing? Choose from {}".format(choice))
	click.echo("Choose a location for saving your {} classes".format(class_.upper()))
	return (class_, filedialog.askdirectory())


@main.command()
@click.option('--config', '-cf', is_flag=True, help="Open the user config file created during setup.")
def setup(config):
	# TODO: Move to different class!
	#user_yml_path = os.path.join(click.get_app_dir("kita"), "user.yml")
	#print(user_yml_path)
	#if os.path.isfile(user_yml_path):
	#	if config:
	#		click.echo("Opening user config file..")
	#		click.launch(user_yml_path)
	#		return
	#	elif not click.confirm("Kita is already set up. Continue anyway?"):
	#		click.echo("\nSetup cancelled.")
	#		return
#
	#data = {}
	#data['user_name'] = click.prompt("Please enter your correct ilias user name").strip()
	#data['password'] = click.prompt("Please enter your ilias password").strip()
#
	#click.echo("Choose a location for saving your assignments")
	#root = tk.Tk()
	#root.withdraw()
	#selected_path = filedialog.askdirectory()
	#data['destination'] = {}
	#data['destination']['root_path'] = selected_path
#
	#click.echo("Downloads will be saved to '{}'.".format(selected_path))
	#os.makedirs(os.path.dirname(user_yml_path), exist_ok=True)
	#with open(user_yml_path, 'w') as path:
	#	yaml.dump(data, path, default_flow_style=False)
#
	#click.echo("\nSetup successful. Type 'kita --help' for details.")

	root_path = 'G:/KIT/Sonstiges/WS18-19'	
	sub_folders = next(os.walk(root_path))[1]

	assignment_folders = []
	for folder in sub_folders:
		path = os.path.join(root_path, folder)
		result = find_assignments_folder(path, folder)
		if result:
			assignment_folders.append(result)

	if assignment_folders:
		click.echo("\nPossible KIT folder detected.")
		for folder in assignment_folders:
			path_msg = os.path.join("root", folder[1])
			message = utils.reformat("Save {} assignments to '{}' folder?".format(folder[0].upper(), path_msg))
			if click.confirm(message):
				print('OK')
				# Set class path
			#else:

		while not click.confirm("Are these all classes for now?"):			
			choice = ', '.join(key for key in all_classes.keys())
			selection = select_folder_manually(choice)
			class_key = selection[0]
			path = selection[1]

			if path:
				# add folder
				config = yaml.load(open('config.yml'))
				class_ = config['classes'][class_key]
				class_['path'] = path

				yaml.compact(seq_seq=False, seq_map=False)

				print("Add {} path {}.".format(class_key, path))
				with open('config.yml', 'w') as cfg_path:
					yaml.dump(config, cfg_path)


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
