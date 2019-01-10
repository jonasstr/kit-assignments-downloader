from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import yaml
import time
import logger

class Scraper:

	def __init__(self, driver, root_path, logger):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 10)
		self.main_page = "https://ilias.studium.kit.edu"
		self.root_path = root_path
		self.logger = logger

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
			time.sleep(0.2)
		# Switch to the new tab
		self.driver.switch_to.window(self.driver.window_handles[-1])

	def download(self, class_, assignment_num):
		'''
		Downloads the specified assignment of the given class.
		'''		
		# Retrieve the assignment name by replacing the 'format' variable of the class dictionary
		# with the specified assignment number and append leading zeroes if necessary
		format = class_['assignment']['format']
		# Split (optional) path in format
		values = format.split('/')
		# If specified, the path comes before the assignment
		path = values[0] if len(values) == 2 else ''
		# If the path has been specifed, the assignment is at [1]
		assignment = values[0] if len(values) == 1 else values[1]
			
		if len(values) > 1:
			num_digits = path.count('$')
			path = path.replace('$' * num_digits, str(assignment_num).zfill(num_digits))
		
		num_digits = assignment.count('$')
		assignment = assignment.replace('$' * num_digits, str(assignment_num).zfill(num_digits))

		with logger.bar("Downloading '{}' from '{}'".format(path + "/" + assignment, class_['name']), True):
			# Open the class page in a new tab (and switch to it as specified in firefox preferences)
			self.click_link(class_['name'], True)
			self.switch_to_last_tab()
			# Click on the assignments folder
			self.click_link(class_['assignment']['name'])

			if path:
				# Click on the additional folder (if specified)
				self.click_link(path)

			# Download the assigment
			self.click_link(assignment)
			time.sleep(1)
			# Close this tab
			self.driver.close()
			self.driver.switch_to.window(self.driver.window_handles[0])
