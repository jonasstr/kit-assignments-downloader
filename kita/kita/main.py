from selenium import webdriver
from logger import Logger
from logging.handlers import RotatingFileHandler
from selenium.webdriver.firefox.options import Options
import kita
import yaml
import click
import traceback
import logging
import sys

with open("config.yml", encoding='utf-8') as config:
	data = yaml.safe_load(config)
	all_classes = data['classes']

def get_options():
	options = Options()
	options.headless = True
	return options

def create_profile():
	'''
	Sets the Firefox preferences
	'''
	profile = webdriver.FirefoxProfile()
	# Download to specified path
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", 'C:\\Users\\Jonas\\Desktop\\testdl')
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

@click.command()
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(all_classes))
@click.argument('assignment_num', required=False)
@click.option("--all", "-a", is_flag=True, help="Download assignments from all specified classes.")
@click.option("--headless/--visible", "-h/-v", default=True,  help="Start the browser in headless mode (no visible UI).")
def main(class_names, assignment_num, all, headless):

	try:
		if not all and not assignment_num:
			int(assignment_num)
	except (ValueError, TypeError):
		print("Assignment number must be an integer!")
		return
	#logger = Logger()
	driver = webdriver.Firefox(firefox_profile=create_profile(), options=get_options() if headless else None)

	scraper = kita.Scraper(driver, data['root_path'])
	classes_to_iterate = all_classes if all else class_names
	
	for name in classes_to_iterate:
		try:
			if 'link' in all_classes[name]:
				scraper.download_from(all_classes[name], assignment_num)
				continue
			elif not scraper.on_any_page(): scraper.to_home()
			scraper.download(all_classes[name], assignment_num)
		except:
			print("Assignment could not be found!")
	print("EXITING")
	driver.quit()

if __name__ == '__main__':
	main()
 