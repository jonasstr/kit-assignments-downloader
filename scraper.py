from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import yaml
import time
import click
import logger

class Scraper:

	def __init__(self, driver, root_path):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 15)
		self.main_page = "https://ilias.studium.kit.edu"
		self.root_path = root_path

	def to_home(self):
		with logger.bar("Opening main page.."):
			self.driver.get(self.main_page)
		
		with logger.bar("Logging in.."):
			# Click on login buttons
			self.driver.find_element_by_link_text('Anmelden').click()
			self.driver.find_element_by_id('f807').click()
		
			with open("config.yml") as config:
				data = yaml.safe_load(config)
				# Fill in login credentials and login
				self.driver.find_element_by_id('name').send_keys(data['user_name'])
				self.driver.find_element_by_id('password').send_keys(data['password'], Keys.ENTER)

	def path_of(self, name: str):
		return "//a[text()='{}' and @class='il_ContainerItemTitle']".format(name)

	def click_link(self, name: str, new_tab=False):
		link = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.path_of(name))))
		if new_tab:
			actions = ActionChains(self.driver)
			actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
		# Click on link without scrolling
		else: self.driver.execute_script("arguments[0].click();", link)

	def switch_to_last_tab(self):
		# Wait until site has loaded
		tabs_before = len(self.driver.window_handles)
		while len(self.driver.window_handles) == tabs_before:
			time.sleep(0.25)
		# Switch to the new tab
		self.driver.switch_to.window(self.driver.window_handles[-1])

	def switch_to_first_tab(self):
		actions = ActionChains(self.driver)
		actions.key_down(Keys.CONTROL).key_up(Keys.CONTROL).perform()
		time.sleep(4)
		self.driver.switch_to.window(self.driver.window_handles[0])

	def download(self, class_, assignment_num):
		'''
		Downloads the specified assignment of the given class.
		'''		# Retrieve the assignment name by replacing the 'format' variable of the class dictionary
		# with the specified assignment number and append leading zeroes if necessary
		assignment = class_['assignment']['format'].replace("$", str(assignment_num).zfill(2))
		with logger.bar("Downloading '{}' from '{}'".format(assignment, class_['name']), True):
			# Open the class page in a new tab (and switch to it as specified in firefox preferences)
			self.click_link(class_['name'], True)
			self.switch_to_last_tab()
			# Click on the assignments folder
			self.click_link(class_['assignment']['name'])
			# Download the assigment
			self.click_link(assignment)
			# Close this tab
			self.driver.close()

	def download_all_of(self, classes, assignment_num):
		#classes_to_iterate = all_classes if all else classes
		for name in classes:
			lecture = all_classes[name]
			self.download(self.wait, lecture, assignment_num)
			# Download assignments
			#for num in range(1, int(assignment_num) + 1):
			self.switch_to_first_tab(self.driver)
