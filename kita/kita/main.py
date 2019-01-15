import logging
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog
import traceback

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from logger import Logger
from logging.handlers import RotatingFileHandler

import click
import kita
import yaml


with open("user.yml", encoding='utf-8') as user:
	user_data = yaml.safe_load(user)
	download_path = user_data['download_path']

with open("config.yml", encoding='utf-8') as config:
	config_data = yaml.safe_load(config)
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
	print("MAIN")

@main.command()
def setup():	
	user_path = os.path.join(click.get_app_dir("kita"), "user.yml")
	print(user_path)
	if os.path.isfile(user_path):
		if not click.confirm("Seems like you already used the 'kita setup' command before. Start again?"):
			return

	data = {}
	data['user_name'] = click.prompt("Please enter your correct ilias user name").strip()
	data['password'] = click.prompt("Please enter your ilias password").strip()

	if click.confirm("Auto-sort and rename your assignments after downloading?"):
		click.echo("Please choose a location for saving your assignments")

		root = tk.Tk()
		root.withdraw()
		selected_path = filedialog.askdirectory()
		print(selected_path)

		os.makedirs(os.path.dirname(root_path), exist_ok=True)
		with open(root_path, 'w') as user_file:
			yaml.dump(data, user_file, default_flow_style=False)

	else:
		click.echo("Please choose a download location for saving your assignments")
		selected_path = filedialog.askdirectory()
		print(selected_path)
		click.echo("\nSetup successful. Type 'kita get' to start.")


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
