from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import time, logger, traceback
import shutil, os
import yaml

class Scraper:

	def __init__(self, driver, download_path, dst):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 4)
		self.main_page = "https://ilias.studium.kit.edu"
		self.download_path = download_path
		self.dst = dst

	def on_any_page(self):
		try:
			return not self.driver.current_url == 'about:blank'
		except Exception as e:
			return False

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
		try:
			link = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.path_of(name))))
			if new_tab:
				actions = ActionChains(self.driver)
				actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
			# Click on link without scrolling
			else: self.driver.execute_script("arguments[0].click();", link)
		except:
			raise

	def switch_to_last_tab(self):
		# Wait until site has loaded
		tabs_before = len(self.driver.window_handles)
		while len(self.driver.window_handles) == tabs_before:
			time.sleep(0.2)
		# Switch to the new tab
		self.driver.switch_to.window(self.driver.window_handles[-1])

	def format_assignment_name(self, format, assignment_num):
		num_digits = format.count('$')
		return format.replace('$' * num_digits, str(assignment_num).zfill(num_digits))

	def download(self, class_, assignment_num):
		'''
		Downloads the specified assignment of the given class.
		'''		
		# Retrieve the assignment name by replacing the 'format' variable of the class dictionary
		# with the specified assignment number and append leading zeroes if necessary
		format = class_['assignment']['format']
		# Split (optional) path in format
		values = format.split('/')
		path = values[0] if len(values) == 2 else ''
		# If the path has been specifed, the assignment is at [1]
		assignment = values[0] if len(values) == 1 else values[1]
			
		if len(values) > 1:
			path = self.format_assignment_name(path, assignment_num)
		assignment = self.format_assignment_name(assignment, assignment_num)

		with logger.bar("Downloading '{}' from '{}'".format(assignment, class_['name']), True):

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
			# Return the name of the downloaded file
			return assignment

	def download_from(self, class_, assignment_num):

		with logger.bar("Opening page specified by link attribute.."):
			self.driver.get(class_['link'])
		
		format = class_['assignment']['format']
		assignment = self.format_assignment_name(format, assignment_num)

		with logger.bar("Downloading '{}' from '{}'".format(assignment, class_['name']), True):
			self.driver.find_element_by_link_text(assignment).click()
			time.sleep(1)
			# Return the name of the downloaded file
			return assignment

	def move_and_rename(self, assignment, class_, assignment_num):

		# If the PDF file name is different from the download link name,
		# this is specified as the 'file_format' value in the config file.
		file_name = assignment
		asgmt = class_['assignment']
		if 'file_format' in asgmt:
			file_name = self.format_assignment_name(asgmt['file_format'], assignment_num)

		#print("FILE NAME: " + file_name)
		src = os.path.join(self.download_path, file_name + ".pdf")	
		dst_folder = os.path.join(self.dst['root_path'], class_['path'])
		dst_file = os.path.join(dst_folder, self.format_assignment_name(self.dst['rename_format'], assignment_num) + ".pdf")

		with logger.bar("Moving assignment to {}".format("root\\" + class_['path']), True):
			shutil.move(src, dst_file)

