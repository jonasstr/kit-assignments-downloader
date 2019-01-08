from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import click
from progressbar import ProgressBar

class Scraper:

	def __init__(self, driver, root_path):
		self.driver = driver
		self.wait = WebDriverWait(self.driver, 10)
		self.main_page = "https://ilias.studium.kit.edu"
		self.root_path = root_path

	def to_home(self):
		bar = ProgressBar("Opening main page..")
		self.driver.get(self.main_page)
		bar.complete()
		
		# Click on login buttons
		self.driver.find_element_by_link_text('Anmelden').click()
		self.driver.find_element_by_id('f807').click()
		
		bar = ProgressBar("Logging in..")
		# Fill in login credentials and login
		self.driver.find_element_by_id('name').send_keys('uzxhf')
		self.driver.find_element_by_id('password').send_keys('sccK1t!?com', Keys.ENTER)
		bar.complete()

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
		self.driver.switch_to.window(self.driver.window_handles[0])

	def download(self, lecture, assignment_num):
		'''
		Downloads the specified assignment of the given lecture.
		'''
		bar = ProgressBar("Downloading assignment {} from class '{}'".format(assignment_num, lecture.name), True)
		# Open the lecture in a new tab (and switch to it as specified in firefox preferences)
		self.click_link(lecture.name, True)
		self.switch_to_last_tab()
		# Click on the assignments folder
		self.click_link(lecture.assignment_num)
		# Download assigment:
		# Retrieve the assignment name by replacing the 'frmt' variable of the lecture
		# with the specified assignment number and append leading zeroes if necessary
		assignment = lecture.frmt.replace("$", str(assignment_num).zfill(2))
		self.click_link(assignment)
		bar.complete()

	def download_all_of(self, all_classes, classes):
		classes_to_iterate = all_classes if all else classes
		for name in classes_to_iterate:
			lecture = all_classes[name]
			self.download(self.wait, lecture, assignment_num)
			# Download assignments
			#for num in range(1, int(assignment_num) + 1):
			self.switch_to_first_tab(self.driver)
