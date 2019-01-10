from selenium import webdriver
from logger import Logger
from logging.handlers import RotatingFileHandler
from scraper import Scraper
import yaml
import click
import traceback

with open("config.yml", encoding='utf-8') as config:
	data = yaml.safe_load(config)
	all_classes = data['classes']

def create_profile():

	'''
	Sets the Firefox preferences
	'''
	# Enable later!
	#options = Options()
	#options.headless = True
	#options=options)

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
@click.argument('assignment_num')
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(all_classes))
@click.option("--all", "-a", is_flag=True, help="Download assignments from all specified classes.")
def main(assignment_num: int, class_names, all):

	logger = Logger()
	driver = webdriver.Firefox(firefox_profile=create_profile())	
	try:
		scraper = Scraper(driver, data['root_path'], logger)
		scraper.to_home()
		classes_to_iterate = all_classes if all else class_names
		for name in classes_to_iterate:
			scraper.download(all_classes[name], assignment_num)
		
	except Exception as e:
		print(str(e))
		print(traceback.format_exc())
		logger.log(e, traceback.format_exc())
		# Close for testing purposes
		driver.close()

if __name__ == '__main__':
	main()
 