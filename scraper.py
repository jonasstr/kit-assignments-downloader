
class Scraper:

	ilias_main = "https://ilias.studium.kit.edu"

	def __init__(self, driver, root_path):
		self.driver
		self.root_path = root_path

	def to_home(self):
		# Open page in new window
		driver.get(ilias_main)
		
		# Click on login button
		driver.find_element_by_link_text('Anmelden').click()
		driver.find_element_by_id('f807').click()
		
		# Fill in login credentials and login
		driver.find_element_by_id('name').send_keys('uzxhf')
		driver.find_element_by_id('password').send_keys('sccK1t!?com', Keys.ENTER)
