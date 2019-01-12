from selenium import webdriver
from logger import Logger
from logging.handlers import RotatingFileHandler
from selenium.webdriver.firefox.options import Options
import traceback, logging, sys
import yaml, click
import kita

with open("config.yml", encoding='utf-8') as config:
	data = yaml.safe_load(config)
	all_classes = data['classes']
	download_path = data['download_path']

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

@click.command()
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(all_classes))
@click.argument('assignment_num', required=False)
@click.option('--move', '-m', is_flag=True, default=True, help="Move the downloaded assignments to the specified directory and rename them.")
@click.option('--all', '-a', is_flag=True, help="Download assignments from all specified classes.")
@click.option('--headless/--visible', '-h/-v', default=True,  help="Start the browser in headless mode (no visible UI).")
def main(class_names, assignment_num, move, all, headless):

	try:
		if not all and not assignment_num:
			int(assignment_num)
	except (ValueError, TypeError):
		print("Assignment number must be an integer!")
		return
	#logger = Logger()
	driver = webdriver.Firefox(firefox_profile=create_profile(), options=get_options() if headless else None)

	scraper = kita.Scraper(driver, download_path, data['destination'])
	classes_to_iterate = all_classes if all else class_names
	
	for name in classes_to_iterate:
		try:
			if 'link' in all_classes[name]:
				scraper.download_from(all_classes[name], assignment_num)
				continue
			elif not scraper.on_any_page(): scraper.to_home()
			class_ = all_classes[name]
			assignment = scraper.download(class_, assignment_num)
			if move:
				scraper.move_and_rename(assignment, class_, assignment_num)
		except (OSError, IOError):
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
	print("EXITING")
	driver.quit()

if __name__ == '__main__':
	main()
