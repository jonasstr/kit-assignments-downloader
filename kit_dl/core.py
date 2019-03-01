import os
import re
import shutil
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from kit_dl.misc import logger
from kit_dl.misc.logger import ProgressLogger, SilentProgressLogger


class Scraper:
    """Implements all webpage related commands such as downloading and moving assignments.
        Constructs a new Scraper and a WebDriverWait object with a default
        maximum waiting time of 10 seconds.
    """

    def __init__(self, driver, dao, verbose):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.main_page = "https://ilias.studium.kit.edu/login.php"
        self.dao = dao
        self.verbose = verbose

    def on_ilias_page(self):
        """Checks whether the selenium webdriver is currently on any webpage."""
        try:
            return self.driver.current_url.startswith("https://ilias.studium.kit.edu")
        except Exception:
            return False

    def to_home(self):
        """Opens the ilias home page and logs the user in with the login
            credentials specified in the user.yml file.
        """
        self.driver.get(self.main_page)
        # Click on login button.
        self.driver.find_element_by_id("f807").click()
        # Fill in login credentials and login.
        self.driver.find_element_by_id("name").send_keys(self.dao.user_data["user_name"])
        self.driver.find_element_by_id("password").send_keys(self.dao.user_data["password"], Keys.ENTER)
        time.sleep(1)
        return "Login fehlgeschlagen" not in self.driver.page_source

    def path_of(self, name):
        """Retrieves the xpath of the link with the specified name on the current webpage.
        Assumes that all assignment and folder HTML elements have the same format.
        """
        return "//a[text()='{}' and @class='il_ContainerItemTitle']".format(name)

    def click_link(self, name, new_tab=False):
        """Clicks on the link with the given text on ilias (either in a new tab or the current one).

        :raises TimeoutException: If the link with the given name could not be found
                after a certain amount of time.
        """

        link = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.path_of(name))))
        if new_tab:
            actions = ActionChains(self.driver)
            # Presses CTRL + left mouse click to open the link in a new tab.
            actions.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
        else:
            self.driver.execute_script("arguments[0].click();", link)

    def switch_to_last_tab(self):
        """Switches to the current last tab in Firefox."""
        # Wait until the site has loaded.
        tabs_before = len(self.driver.window_handles)
        while len(self.driver.window_handles) == tabs_before:
            time.sleep(0.1)
        # Switch to the new tab.
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def download(self, course, assignment_num):
        """Downloads the specified assignment of the given class from ilias.

        Retrieves the assignment name by replacing the format attribute of the given course
        as specified in the config.yml file with the specified assignment number
        and append leading zeroes if necessary.

        The format attribute may contain an optional previous path name separated by
        a single '/', which will be moved to before downloading the assignment.
        """
        link_format = course["assignment"]["link_format"]
        assignment = self.get_assignment_to_download(assignment_num, link_format)
        optional_path = self.get_optional_path(assignment_num, link_format)
        self.perform_download_on_site(course, optional_path, assignment)
        return assignment

    def perform_download_on_site(self, course, optional_path, assignment):
        # Open the course page in a new tab (and switch to it as specified in firefox preferences).
        self.click_link(course["name"], True)
        self.switch_to_last_tab()
        # Click on the assignments folder.
        self.click_link(course["assignment"]["link_name"])
        if optional_path:
            self.click_link(optional_path)
        # Download the assigment.
        self.click_link(assignment)
        time.sleep(1)
        # Close this tab.
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_assignment_to_download(self, assignment_num, format):
        values = format.split("/")
        # If the path has been specified, the assignment is at [1]
        assignment = values[0] if len(values) == 1 else values[1]
        return self.format_assignment_name(assignment, assignment_num)

    def get_optional_path(self, assignment_num, format):
        values = format.split("/")
        if len(values) == 2:
            return self.format_assignment_name(values[0], assignment_num)

    def format_assignment_name(self, name, assignment_num):
        """Formats the specified assignment name by replacing all $-signs with the assignment number.
        Appends leading zeroes if the amount of consecutive $-signs is higher than
        the assignment number.
        """
        num_digits = name.count("$")
        return name.replace("$" * num_digits, str(assignment_num).zfill(num_digits))

    def download_from(self, course, assignment_num):
        """Provides the ability to download an assignment from a different source than ilias.

        The external link must be specified as the link attribute in the config.yml file of the given course.
        Uses the assignment:format attribute in the config.yml file to determine the name of the link
        of the assignment to download.
        """
        self.driver.get(course["link"])
        format = course["assignment"]["link_format"]
        assignment = self.format_assignment_name(format, assignment_num)

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

        msg = "\nMoving to {}".format(dst_folder)
        with logger.strict(msg, self.verbose):
            shutil.move(src, dst_file)

    def download_default(self, course, assignment_num, move, rename_format=None):
        assignment = None
        if "link" in course:
            assignment = self.download_from(course, assignment_num)
        else:
            if not self.on_ilias_page():
                if not self.to_home():
                    return False
            assignment = self.download(course, assignment_num)
        if move:
            if not rename_format:
                rename_format = self.dao.user_data["destination"]["rename_format"]
            self.move_and_rename(assignment, course, assignment_num, rename_format)
        return True

    def update_directory(self, course, course_name):
        """Downloads the latest assignments for the given course."""
        course_dir = os.path.join(self.dao.user_data["destination"]["root_path"], course["path"])
        assignment_files = next(os.walk(course_dir))[2]
        rename_format = self.find_rename_format(course)
        latest_assignment = self.get_latest_assignment(assignment_files, rename_format)
        if self.verbose:
            print(
                self.get_on_start_update_msg(course_name, latest_assignment, rename_format),
                flush=False,
                end="\n",
            )
        self.perform_update(course, course_name, latest_assignment, rename_format)

    def get(self, course, course_name, assignment_nums, move):
        rename_format = self.find_rename_format(course)
        try:
            with self.get_specific_logger(course_name, rename_format) as logger:
                for num in assignment_nums:
                    logger.update(num)
                    if not self.download_default(course, num, move, rename_format):
                        raise LoginException(
                            "Login failed! Use 'kit-dl setup --user' and update username and password."
                        )
        except (IOError, OSError):
            print("Invalid destination path for this assignment!")
        except (TimeoutException, NoSuchElementException, LoginException) as e:
            if str(e).endswith("Message: "):
                print(str(e).replace("Message: ", "Error: "))

    def get_on_start_update_msg(self, course_name, latest_assignment, rename_format):
        """Returns the start message that will be printed during update."""
        if latest_assignment > 0:
            assignment = self.format_assignment_name(rename_format, latest_assignment)
            return "Updating {} assignments, latest: {}".format(course_name.upper(), assignment + ".pdf")
        else:
            return "No assignments found in {} directory, starting at 1.".format(course_name.upper())

    def get_specific_logger(self, course_name, rename_format):
        return (
            ProgressLogger(course_name.upper(), rename_format)
            if self.verbose
            else SilentProgressLogger(course_name.upper())
        )

    def perform_update(self, course, course_name, latest_assignment, rename_format):
        try:
            with self.get_specific_logger(course_name, rename_format) as logger:
                while True:
                    logger.update(latest_assignment + 1)
                    if not self.download_default(course, latest_assignment + 1, True, rename_format):
                        raise LoginException(
                            "Login failed! Use 'kit-dl setup --user' and update username and password."
                        )
                    latest_assignment += 1
        except (IOError, OSError):
            print("Invalid destination path for this assignment!")
        except (TimeoutException, NoSuchElementException, LoginException) as e:
            if str(e).endswith("Message: "):
                print(str(e).replace("Message: ", "Error: "))

    def get_latest_assignment(self, assignment_files, rename_format):
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
        if re.search(r"^\d+$", result):
            return int(result)

    def find_rename_format(self, course):
        course_dir = os.path.join(self.dao.user_data["destination"]["root_path"], course["path"])
        assignment_files = next(os.walk(course_dir))[2]
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


class LoginException(Exception):
    pass
