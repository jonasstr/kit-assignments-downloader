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
	"""The core class of kita, implements all CLI commands.

	Creates a new Scraper and a WebDriverWait object with a default 
	maximum waiting time of 10 seconds.

	Args: 
		driver: The selenium webdriver to use.
		download_path (str): The path where all Firefox downloads will be stored.
			If the move flag is active, kita will look for the downloaded files
			in this directory if the move_and_rename method is called later.
		dst (dict): The dictionary in user.yml specifiying the root_path used for
			move_and_rename as well as the format specifying how all files should be renamed.

	"""

	def __init__(self, driver, user_data):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 10)
		self.main_page = "https://ilias.studium.kit.edu"
		self.user_data = user_data
		self.download_path = user_data['download_path']
		self.dst = user_data['destination']

	def on_any_page(self):
		"""
		Returns: 
			Whether the selenium webdriver is currently on any webpage.

		"""
		try:
			return not self.driver.current_url == 'about:blank'
		except Exception as e:
			return False

	def to_home(self):
		"""Opens the ilias home page and logs the user in with the login
			credentials specified in the user.yml file.

		"""
		with logger.bar("Opening main page.."):
			self.driver.get(self.main_page)
		
		with logger.bar("Logging in.."):
			# Click on login buttons.
			self.driver.find_element_by_link_text('Anmelden').click()
			self.driver.find_element_by_id('f807').click()
		
			# Fill in login credentials and login.
			self.driver.find_element_by_id('name').send_keys(self.user_data['user_name'])
			self.driver.find_element_by_id('password').send_keys(self.user_data['password'], Keys.ENTER)

	def path_of(self, name):
		"""Retrieves the xpath of the link with the specified name on the current webpage.
		Assumes that all assignment and folder HTML elements have the same format. 

		Args:
			name (str): The link text to return the xpath of.

		Returns:
			The xpath to the link specified by the name argument. 
		"""
		return "//a[text()='{}' and @class='il_ContainerItemTitle']".format(name)

	def click_link(self, name, new_tab=False):
		"""Clicks on the link with the given text on ilias (either in a new tab or the current one).

		Args:
			name: The link text to search for.
			new_tab (bool): Whether to open the link in a new tab. Defaults to False.

		Raises:
			TimeoutException: If the link with the given name could not be found 
				after a certain	amount of time.
		"""
		try:
			link = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.path_of(name))))
			if new_tab:
				actions = ActionChains(self.driver)
				# Presses CTRL + left mouse click to open the link in a new tab.
				actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
			else: self.driver.execute_script("arguments[0].click();", link)
		except:
			raise

	def switch_to_last_tab(self):
		"""Switches to the current last tab in Firefox.

		"""
		# Wait until the site has loaded.
		tabs_before = len(self.driver.window_handles)
		while len(self.driver.window_handles) == tabs_before:
			time.sleep(0.2)
		# Switch to the new tab.
		self.driver.switch_to.window(self.driver.window_handles[-1])

	def format_assignment_name(self, name, assignment_num):
		"""Formats the specified assignment name by replacing all $-signs with the assignment
		number (appends leading zeroes if the amount of consecutive $-signs is higher than
		the assignment number).
	
		Args:
			name: The name of the assignment to format. All $-signs will be replaced
				by the assignment number and leading zeroes if necessary.
			assignment_num (int): The number of the assignment to replace the $-signs.

		"""
		num_digits = name.count('$')
		return name.replace('$' * num_digits, str(assignment_num).zfill(num_digits))

	def download(self, class_, assignment_num):
		"""Downloads the specified assignment of the given class from ilias.

		Retrieves the assignment name by replacing the format attribute of the given class
		as specified in the config.yml file with the specified assignment number 
		and append leading zeroes if necessary.

		The format attribute may contain an optional previous path name separated by
		a single '/', which will be moved to before downloading the assignment.
		
		Args:
			class_: The class retrieved from config.yml to download.
			assignment_num (int): The number of the assignment to download.

		Returns:
			str: The name of the link of the downloaded assignment.

		"""
		format = class_['assignment']['format']
		# Split (optional) path in format.
		values = format.split('/')
		# If the path has been specifed, the assignment is at [1]
		assignment = values[0] if len(values) == 1 else values[1]
		assignment = self.format_assignment_name(assignment, assignment_num)

		path = ''
		if len(values) == 2:
			path = self.format_assignment_name(values[0], assignment_num)

		with logger.bar("Downloading '{}' from '{}'".format(assignment, class_['name']), True):
			# Open the class page in a new tab (and switch to it as specified in firefox preferences).
			self.click_link(class_['name'], True)
			self.switch_to_last_tab()
			# Click on the assignments folder.
			self.click_link(class_['assignment']['link_name'])
			if path:
				# Click on the additional folder (if specified).
				self.click_link(path)
			# Download the assigment.
			self.click_link(assignment)
			time.sleep(1)
			# Close this tab.
			self.driver.close()
			self.driver.switch_to.window(self.driver.window_handles[0])
			return assignment

	def download_from(self, class_, assignment_num):
		"""Provides the ability to download an assignment from a different source than ilias.

		The external link must be specified as the link attribute in the config.yml file of the given class.
		Uses the assignment:format attribute in the config.yml file to determine the name of the link
		of the assignment to download.

		Args:
			class_: The class retrieved from the config.yml file. Must include
				a link attribute to specify the main url of the external site.
			assignment_num (int): The number of the assignment to download.

		Returns:
			str: The name of the link of the downloaded assignment.
		"""

		with logger.bar("Opening page specified by link attribute.."):
			self.driver.get(class_['link'])
		
		format = class_['assignment']['format']
		assignment = self.format_assignment_name(format, assignment_num)

		with logger.bar("Downloading '{}' from '{}'".format(assignment, class_['name']), True):
			self.driver.find_element_by_link_text(assignment).click()
			time.sleep(1)
			return assignment

	def move_and_rename(self, assignment, class_, assignment_num):
		"""Moves and renames a downloaded assignment PDF to the specified destination folder.

		Assumes that the name of the PDF is the same as the link of the assignment. If 
		the file name is different, this must be specified as the file_format attribute of the 
		given class in the config.yml file. The format_assignment_name method will then be used
		to retrieve the correct file name.
		
		The file will be copied to the folder specified by the path attribute of the class
		in the config.yml file relative to the root_path as specified in the user.yml file. 

		It will be renamed based on the destination/rename_format attribute
		specified in the user.yml file.

		Args:
			assignment (str): The name of the link text of the downloaded assignment.
				By default, this method will search for a PDF file with this name.
			class_ (dict): The previously downloaded class retrieved from the config.yml
				file. Specifies the (optional) file format of the assignment PDF and 
				the path to copy it to.
			assignment_num (int): The assignment number of the downloaded assignment file.
		"""

		file_name = assignment
		asgmt = class_['assignment']
		if 'file_format' in asgmt:
			file_name = self.format_assignment_name(asgmt['file_format'], assignment_num)

		src = os.path.join(self.download_path, file_name + ".pdf")	
		dst_folder = os.path.join(self.dst['root_path'], class_['path'])
		dst_file = os.path.join(dst_folder, self.format_assignment_name(self.dst['rename_format'], assignment_num) + ".pdf")

		with logger.bar("Moving assignment to {}".format("root\\" + class_['path']), True):
			shutil.move(src, dst_file)

	def get(self, class_, assignment_num, move):
		assignment = None
		if 'link' in class_:
			assignment = self.download_from(class_, assignment_num)
		else:
			if not self.on_any_page(): self.to_home()
			assignment = self.download(class_, assignment_num)
		if move:
			self.move_and_rename(assignment, class_, assignment_num)

	def latest_assignment(self, class_dir):
		"""Finds the currently latest assignment in a given user directory.
		
		Args:
			class_dir (dict): The absolute path to the class directory to search in.

		Returns:
			int: The latest assignment number, 0 if no file matched the rename_format.
		"""

		rename_format = self.dst['rename_format'] + ".pdf"
		current_assignment = 1
		latest_assignment = None
		while latest_assignment == None:
			assignment_path = os.path.join(class_dir, self.format_assignment_name(rename_format, current_assignment))
			# Search for the current assignment PDF.
			if not os.path.isfile(assignment_path):
				latest_assignment = current_assignment - 1
			else: current_assignment += 1
		return latest_assignment

	def update_directory(self, class_):

		class_dir = os.path.join(self.dst['root_path'], class_['path'])
		latest = self.latest_assignment(class_dir)

		if (latest > 0):
			assignment = self.format_assignment_name(self.dst['rename_format'], latest)
			print("Detected latest assignment: {}".format(assignment))
		else: print("No assignments found in given directory")

		try:
			while (True):
				self.get(class_, latest + 1, True)
				latest += 1
		except (IOError, OSError):
			print("Invalid destination path for this assignment!")
		except:
			raise
			print("Assignment could not be found!")
