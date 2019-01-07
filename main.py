#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import click
import time
import scraper

class Lecture:

	def __init__(self, name, assignment, frmt, folder_name):
		self.name = name
		self.assignment = assignment
		self.frmt = frmt
		self.folder_name = folder_name

root_path = "G:\\KIT\\Sonstiges\\WS18-19" 
la = Lecture("Lineare Algebra 1", "Übungen", "Blatt$", "Lineare Algebra I")
gbi = Lecture("Grundbegriffe der Informatik (2018/2019)", "Übungsblätter", "$-aufgaben", "Grundbegriffe der Informatik")
all_classes = ['la', 'gbi']

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

def click_link(driver, wait: WebDriverWait, name: str, new_tab=False):
	link = wait.until(EC.element_to_be_clickable((By.XPATH, path_of(name))))
	if new_tab:
		actions = ActionChains(driver)
		actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
	# Click on link without scrolling
	else: driver.execute_script("arguments[0].click();", link)

def switch_to_last_tab(driver):
	# Wait until site has loaded
	tabs_before = len(driver.window_handles)
	while len(driver.window_handles) == tabs_before:
		time.sleep(0.25)
	# Switch to the new tab
	driver.switch_to.window(driver.window_handles[-1])

def switch_to_first_tab(driver):
	actions = ActionChains(driver)
	actions.key_down(Keys.CONTROL).key_up(Keys.CONTROL).perform()
	driver.switch_to.window(driver.window_handles[0])

def download(driver, wait, lecture: Lecture, num: int):
	# Open the lecture in a new tab (and switch to it as specified in firefox preferences)
	click_link(driver, wait, lecture.name, True)
	switch_to_last_tab(driver)
	# Click on the assignments folder
	click_link(driver, wait, lecture.assignment)
	# Download assigment:
	# Retrieve the assignment name by replacing the 'frmt' variable of the lecture
	# with the specified assignment number and append leading zeroes if necessary
	assignment = lecture.frmt.replace("$", str(num).zfill(2))
	click_link(driver, wait, assignment)

@click.command()
@click.argument('assignment_num')
@click.argument('class_names', nargs=-1, required=False, type=click.Choice(all_classes))
@click.option("--all", "-a", is_flag=True, default=True, help="Download assignments from all specified classes.")
def main(assignment_num: int, class_names, all):

	driver = webdriver.Firefox(firefox_profile=create_profile())	
	scraper = Scraper(driver)

	scraper.to_home()

	wait = WebDriverWait(driver, 10)
	classes_to_iterate = all_classes if all else class_names
	for name in classes_to_iterate:
		lecture = globals()[name]
		download(driver, wait, lecture, assignment_num)
		# Download assignments
		#for num in range(1, int(assignment_num) + 1):
		switch_to_first_tab(driver)
		
	
	print('Success')
	#driver.close()

if __name__ == '__main__':
	main()
