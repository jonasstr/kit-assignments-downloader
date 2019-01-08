from selenium import webdriver

import click
import time
from scraper import Scraper
from lecture import Lecture

root_path = "G:\\KIT\\Sonstiges\\WS18-19" 
classes = {}
classes['la'] = Lecture("Lineare Algebra 1", "Übungen", "Blatt$", "Lineare Algebra I")
classes['gbi'] = Lecture("Grundbegriffe der Informatik (2018/2019)", "Übungsblätter", "$-aufgaben", "Grundbegriffe der Informatik")

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
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(classes))
@click.option("--all", "-a", is_flag=True, default=True, help="Download assignments from all specified classes.")
def main(assignment_num: int, class_names, all):

	driver = webdriver.Firefox(firefox_profile=create_profile())	
	
	try:
		scraper = Scraper(driver, root_path)
		scraper.to_home()

		scraper.download(classes['la'], 9)
	except:
		# Close for testing purposes
		driver.close()

if __name__ == '__main__':
	main()
	