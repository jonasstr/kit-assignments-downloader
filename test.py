from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

ilias_main = "https://ilias.studium.kit.edu"
# Open page in new window
driver = webdriver.Firefox()
driver.get(ilias_main)

# Click on login buttons
driver.find_element_by_link_text('Anmelden').click()

driver.find_element_by_id('f807').click()

# Fill in login credentials and login
driver.find_element_by_id('name').send_keys('uzxhf')
driver.find_element_by_id('password').send_keys('sccK1t!?com', Keys.ENTER)

# Click on 'Lineare Algebra 1'
#TODO: wait until
driver.implicitly_wait(4)

#wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(.,'Lineare')]"))).click()
driver.find_element_by_xpath("//a[contains(.,'Lineare') and @class='il_ContainerItemTitle']").click()

# Click on 'Übungen'
driver.find_element_by_link_text(u"Übungen").click()

print('Success')
#driver.close()