#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import click

class Lecture:

	def __init__(self, name, assignment, frmt, folder_name):
		self.name = name
		self.assignment = assignment
		self.frmt = frmt
		self.folder_name = folder_name

ilias_main = "https://ilias.studium.kit.edu"
root_path = "G:\\KIT\\Sonstiges\\WS18-19" 
la = Lecture("Lineare Algebra 1", "Übungen", "Blatt$$", "Lineare Algebra I")
gbi = Lecture("Grundbegriffe der Informatik (2018/2019)", "Übungsblätter", "$$-aufgaben", "Grundbegriffe der Informatik")

def create_profile():

	# Enable later!
	#options = Options()
	#options.headless = True
	#options=options)

	profile = webdriver.FirefoxProfile()
	# Set Firefox preferences
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

def path_of(name: str):
	return "//a[text()='{}' and @class='il_ContainerItemTitle']".format(name)

def click_link(driver, wait: WebDriverWait, name: str, actions: ActionChains=None):
	link = wait.until(EC.element_to_be_clickable((By.XPATH, path_of(name))))
	if actions is not None:
		actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
	else: 
		link.click()

	driver.implicitly_wait(5)
	print(len(driver.window_handles))
	# Set the driver to the new tab
	driver.switch_to.window(driver.window_handles[-1])

def first_tab(actions: ActionChains):
	actions.key_down(Keys.CONTROL).key_down(Keys.NUMPAD1).key_up(Keys.TAB).key_up(Keys.NUMPAD1).perform()


@click.command()
@click.argument('assignment_num')
#@click.option('-la', is_flag=True)
@click.argument('class_names', nargs=-1, type=click.Choice(['la', 'gbi', 'prg']))
def main(assignment_num: str, class_names):

	lecture = globals()[class_names[0]]
	print(lecture.assignment)

	driver = webdriver.Firefox(firefox_profile=create_profile())	
	# Open page in new window
	driver.get(ilias_main)
	
	# Click on login button
	driver.find_element_by_link_text('Anmelden').click()
	driver.find_element_by_id('f807').click()
	
	# Fill in login credentials and login
	driver.find_element_by_id('name').send_keys('uzxhf')
	driver.find_element_by_id('password').send_keys('sccK1t!?com', Keys.ENTER)

	wait = WebDriverWait(driver, 10)
	actions = ActionChains(driver)
	for name in class_names:
		lecture = globals()[name]
		# Open the link in a new tab and move to it (see create_profile())
		click_link(driver, wait, lecture.name, actions)
		# Click on the assignments folder
		#click_link(driver, wait, lecture.assignment)
		# Find assignment and download it
		#assignment = driver.find_element_by_xpath(path_of("Blatt0{}".format(assignment_num)))
		#driver.execute_script("arguments[0].click();", assignment)
		# Move to first tab
		#first_tab(actions)
	
	print('Success')
	#driver.close()

if __name__ == '__main__':
	main()
