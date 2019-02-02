import os
import re
import shutil
import time
import traceback

import click
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from kita.misc import logger


class Scraper:
    """Implements all webpage related commands such as downloading and moving assignments.
        Constructs a new Scraper and a WebDriverWait object with a default
        maximum waiting time of 10 seconds.

    :param driver: The selenium webdriver to use.
    :param download_path: The path where all Firefox downloads will be stored.
            If the move flag is active, kita will look for the downloaded files
            in this directory if the move_and_rename method is called later.
    :type download_path: str
    :param dst: The dictionary in user.yml specifiying the root_path used for
            move_and_rename as well as the format specifying how all files should be renamed.
    :type dst: dict

    """

    def __init__(self, driver, dao, verbose):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.main_page = "https://ilias.studium.kit.edu/login.php"
        self.dao = dao
        self.verbose = verbose

    def on_any_page(self):
        """


        :returns: Whether the selenium webdriver is currently on any webpage.

        """
        try:
            return not self.driver.current_url == "about:blank"
        except Exception as e:
            return False

    def to_home(self):
        """Opens the ilias home page and logs the user in with the login
            credentials specified in the user.yml file.
        """
        msg = self.msg("Opening main page and logging in..\n")
        with logger.bar(msgs, self.verbose):
            self.driver.get(self.main_page)
            # Click on login button.
            self.driver.find_element_by_id("f807").click()
            # Fill in login credentials and login.
            self.driver.find_element_by_id("name").send_keys(self.dao.user_data["user_name"])
            self.driver.find_element_by_id("password").send_keys(self.dao.user_data["password"], Keys.ENTER)

    def path_of(self, name):
        """Retrieves the xpath of the link with the specified name on the current webpage.
        Assumes that all assignment and folder HTML elements have the same format.

        :param name: The link text to return the xpath of.
        :type name: str
        :returns: The xpath to the link specified by the name argument.
        """
        return "//a[text()='{}' and @class='il_ContainerItemTitle']".format(name)

    def click_link(self, name, new_tab=False):
        """Clicks on the link with the given text on ilias (either in a new tab or the current one).

        :param name: The link text to search for.
        :param new_tab: Whether to open the link in a new tab. Defaults to False.
        :type new_tab: bool
        :raises TimeoutException: If the link with the given name could not be found
                after a certain amount of time.

        """
        try:
            link = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.path_of(name))))
            if new_tab:
                actions = ActionChains(self.driver)
                # Presses CTRL + left mouse click to open the link in a new tab.
                actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
            else:
                self.driver.execute_script("arguments[0].click();", link)
        except:
            raise

    def switch_to_last_tab(self):
        """Switches to the current last tab in Firefox."""
        # Wait until the site has loaded.
        tabs_before = len(self.driver.window_handles)
        while len(self.driver.window_handles) == tabs_before:
            time.sleep(0.2)
        # Switch to the new tab.
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def download(self, course, assignment_num):
        """Downloads the specified assignment of the given class from ilias.
        
        Retrieves the assignment name by replacing the format attribute of the given course
        as specified in the config.yml file with the specified assignment number
        and append leading zeroes if necessary.
        
        The format attribute may contain an optional previous path name separated by
        a single '/', which will be moved to before downloading the assignment.

        :param course: The course retrieved from config.yml to download.
        :param assignment_num: The number of the assignment to download.
        :type assignment_num: int
        :returns: The name of the link of the downloaded assignment.
        :rtype: str

        """
        format = course["assignment"]["link_format"]
        # Split (optional) path in format.
        values = format.split("/")
        # If the path has been specifed, the assignment is at [1]
        assignment = values[0] if len(values) == 1 else values[1]
        assignment = self.format_assignment_name(assignment, assignment_num)

        path = ""
        if len(values) == 2:
            path = self.format_assignment_name(values[0], assignment_num)

        # msg = self.msg("Downloading '{}' from {}".format(assignment, course['name']))
        with logger.bar("Downloading '{}' from {}".format(assignment, course["name"]), show_done=True):
            # Open the course page in a new tab (and switch to it as specified in firefox preferences).
            self.click_link(course["name"], True)
            self.switch_to_last_tab()
            # Click on the assignments folder.
            self.click_link(course["assignment"]["link_name"])
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

    def msg(self, verbose, silent=None):
        return {"verbose": verbose, "silent": silent}

    def format_assignment_name(self, name, assignment_num):
        """Formats the specified assignment name by replacing all $-signs with the assignment
        number.
        Appends leading zeroes if the amount of consecutive $-signs is higher than
        the assignment number.

        :param name: The name of the assignment to format. All $-signs will be replaced
                by the assignment number and leading zeroes if necessary.
        :param assignment_num: The number of the assignment to replace the $-signs.
        :type assignment_num: int

        """
        num_digits = name.count("$")
        return name.replace("$" * num_digits, str(assignment_num).zfill(num_digits))

    def download_from(self, course, assignment_num):
        """Provides the ability to download an assignment from a different source than ilias.
        
        The external link must be specified as the link attribute in the config.yml file of the given course.
        Uses the assignment:format attribute in the config.yml file to determine the name of the link
        of the assignment to download.

        :param course: The course retrieved from the config.yml file. Must include
                a link attribute to specify the main url of the external site.
        :param assignment_num: The number of the assignment to download.
        :type assignment_num: int
        :returns: The name of the link of the downloaded assignment.
        :rtype: str

        """
        self.driver.get(course["link"])
        format = course["assignment"]["link_format"]
        assignment = self.format_assignment_name(format, assignment_num)

        with logger.bar("Downloading '{}' from {}".format(assignment, course["name"]), True):
            self.driver.find_element_by_link_text(assignment).click()
            time.sleep(1)
            return assignment

    def move_and_rename(self, assignment, course, assignment_num, rename_format):
        """Moves and renames a downloaded assignment PDF to the specified destination folder.
        
        Assumes that the name of the PDF is the same as the link of the assignment. If
        the file name is different, this must be specified as the file_format attribute of the
        given course in the config.yml file. The format_assignment_name method will then be used
        to retrieve the correct file name.
        
        The file will be copied to the folder specified by the path attribute of the course
        in the config.yml file relative to the root_path as specified in the user.yml file.
        
        It will be renamed based on the destination/rename_format attribute
        specified in the user.yml file.

        :param assignment: The name of the link text of the downloaded assignment.
            By default, this method will search for a PDF file with this name.
        :type assignment: str
        :param course: The previously downloaded course retrieved from the config.yml
            file. Specifies the (optional) file format of the assignment PDF and
            the path to copy it to.
        :type course: dict
        :param assignment_num: The assignment number of the downloaded assignment file.
        :type assignment_num: int

        """
        if not rename_format:
            rename_format = self.dao.user_data["destination"]["rename_format"]
        file_name = assignment
        if "file_format" in course["assignment"]:
            file_name = self.format_assignment_name(course["assignment"]["file_format"], assignment_num)

        src = os.path.join(self.dao.user_data["destination"]["root_path"], file_name + ".pdf")
        dst_folder = os.path.join(self.dao.user_data["destination"]["root_path"], course["path"])
        dst_file = os.path.join(
            dst_folder, self.format_assignment_name(rename_format, assignment_num) + ".pdf"
        )

        with logger.bar("Moving assignment to {}".format(dst_folder), True):
            shutil.move(src, dst_file)

    def get(self, course, assignment_num, move, rename_format=None):
        """

        :param course: 
        :param assignment_num: 
        :param move: 
        """
        assignment = None
        if "link" in course:
            assignment = self.download_from(course, assignment_num)
        else:
            if not self.on_any_page():
                self.to_home()
            assignment = self.download(course, assignment_num)
        if move:
            if not rename_format:
                rename_format = self.dao.user_data["destination"]["rename_format"]
            self.move_and_rename(assignment, course, assignment_num, rename_format)

    def update_directory(self, course, course_name):
        """

        :param course: 
        :param course_name: 
        """
        course_dir = os.path.join(self.dao.user_data["destination"]["root_path"], course["path"])
        assignment_files = next(os.walk(course_dir))[2]
        rename_format = self.find_rename_format(assignment_files)
        latest_assignment = self.latest_assignment(assignment_files, rename_format)

        if latest_assignment > 0:
            assignment = self.format_assignment_name(rename_format, latest_assignment)
            print("Detected latest {} assignment: {}".format(course_name.upper(), assignment + ".pdf"))
        else:
            print("No assignments found in {} directory, starting at 1.".format(course_name.upper()))

        try:
            while True:
                self.get(course, latest_assignment + 1, True, rename_format)
                latest_assignment += 1
        except (IOError, OSError):
            print("Invalid destination path for this assignment!")
        except:
            print("Assignment not found!")

    def latest_assignment(self, assignment_files, rename_format):
        """Finds the latest assignment in a list of assignment PDFs."""
        current_assignment = 0
        for assignment in assignment_files:
            diff = [
                asgmt_char
                for i, (asgmt_char, frmt_char) in enumerate(
                    zip(self.remove_extension(assignment), rename_format)
                )
                if asgmt_char != frmt_char
            ]
            num = self.assignment_num_from_diff("".join(diff))
            if num and num > current_assignment:
                current_assignment = num
        return current_assignment

    def assignment_num_from_diff(self, diff):
        result = diff.replace("-", "").strip()
        if result.startswith("0"):
            result = result.replace("0", "")
        if re.search("^\d+$", result):
            return int(result)

    def find_rename_format(self, assignment_files):
        detected_format = self.detect_format(assignment_files)
        return detected_format if detected_format else self.dao.user_data["destination"]["rename_format"]

    def detect_format(self, assignment_files):

        for assignment in assignment_files:
            assignment = self.remove_extension(assignment)
            # If the file name ends with at least one digit replace them with $-signs to get the format.
            num_digits = sum(char.isdigit() for char in assignment)
            if num_digits > 0:
                return re.sub(r"\d+$", "$" * num_digits, assignment)

    def remove_extension(self, file_name):
        return file_name[:-4]
