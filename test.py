#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import click

def create_profile():

	# Enable later!
	#options = Options()
	#options.headless = True
	#options=options)

	profile = webdriver.FirefoxProfile()
	# Preferences to download to specified path
	profile.set_preference("browser.download.folderList", 2)
	profile.set_preference("browser.download.manager.showWhenStarting", False)
	profile.set_preference("browser.download.dir", 'C:\\Users\\Jonas\\Desktop\\testdl')
	
	# Preferences to download PDF files without asking the user
	profile.set_preference("pdfjs.disabled", True)
	profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf")
	profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
	return profile

def path_of(name: str):
	return "//a[text()='" + name + "' and @class='il_ContainerItemTitle']"

@click.command()
@click.argument('assignment_num')
@click.option('-la', is_flag=True, help="Download 'Lineare Algebra 1' assignments.")
def main(assignment_num: str, la):
	driver = webdriver.Firefox(firefox_profile=create_profile())
	wait = WebDriverWait(driver, 10)
	
	# Open page in new window
	ilias_main = "https://ilias.studium.kit.edu"
	driver.get(ilias_main)
	
	# Click on login buttons
	driver.find_element_by_link_text('Anmelden').click()
	driver.find_element_by_id('f807').click()
	
	# Fill in login credentials and login
	driver.find_element_by_id('name').send_keys('uzxhf')
	driver.find_element_by_id('password').send_keys('sccK1t!?com', Keys.ENTER)
	
	# Click on 'Lineare Algebra 1'
	if lin_alg:
		wait.until(EC.element_to_be_clickable((By.XPATH, path_of("Lineare Algebra 1")))).click()
	
	# Click on 'Übungen'
	wait.until(EC.element_to_be_clickable((By.XPATH, path_of("Übungen")))).click()
	
	# Find assignment and download it
	assignment = driver.find_element_by_xpath(path_of("Blatt0{}".format(assignment_num)))
	driver.execute_script("arguments[0].click();", assignment)
	
	print('Success')
	#driver.close()

if __name__ == '__main__':
	main()