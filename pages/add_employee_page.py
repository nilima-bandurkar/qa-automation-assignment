"""PIM > Add Employee form."""

from selenium.common.exceptions import ElementNotInteractableException, TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class AddEmployeePage(BasePage):

    FIRST_NAME = (By.NAME, "firstName")
    LAST_NAME = (By.NAME, "lastName")
    # This field has no id/name, so it is found using its visible label.
    EMPLOYEE_ID = (
        By.XPATH,
        "//label[normalize-space()='Employee Id']"
        "/ancestor::div[contains(@class,'oxd-input-group')]//input",
    )
    PROFILE_PICTURE = (By.CSS_SELECTOR, "input[type='file']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    FORM_HEADER = (By.XPATH, "//h6[normalize-space()='Add Employee']")
    PERSONAL_DETAILS_HEADER = (By.XPATH, "//h6[normalize-space()='Personal Details']")
    EMPLOYEE_NAME = (By.CSS_SELECTOR, ".orangehrm-edit-employee-name h6")

    def is_loaded(self):
        loaded = self.is_displayed(self.FORM_HEADER)
        self.wait_for_loaders()
        return loaded

    def enter_first_name(self, value):
        self.type_text(self.FIRST_NAME, value)
        return self

    def enter_last_name(self, value):
        self.type_text(self.LAST_NAME, value)
        return self

    def enter_employee_id(self, value):
        """The field is pre-filled and allows only 10 characters, so the value
        is checked after typing."""
        self.type_text(self.EMPLOYEE_ID, value)
        actual = self.get_value(self.EMPLOYEE_ID)
        assert actual == value, f"Employee Id field shows '{actual}' instead of '{value}'"
        return self

    def upload_profile_picture(self, image_path):
        """Send the file path to the hidden file input."""
        self.log.info("Upload profile picture: %s", image_path.name)
        upload = self.wait_for_present(self.PROFILE_PICTURE)
        try:
            upload.send_keys(str(image_path))
        except ElementNotInteractableException:
            # The app hides the real input behind a button.
            self.driver.execute_script(
                "arguments[0].style.display='block';arguments[0].style.visibility='visible';",
                upload,
            )
            upload.send_keys(str(image_path))
        return self

    def save_employee(self):
        self.log.info("Save employee")
        self.click(self.SAVE_BUTTON)
        self.wait_for_loaders()

    def verify_employee_created(self, expected_name):
        """After a successful save the app opens the new employee's page."""
        toast = self.get_toast_message(timeout=8)
        if toast:
            self.log.info("Message: %s", toast.replace("\n", " "))
        try:
            self.wait_for_url_contains("/pim/viewPersonalDetails/empNumber/")
        except TimeoutException:
            self.log.error("Employee page did not open after save")
            return False
        if not self.is_displayed(self.PERSONAL_DETAILS_HEADER):
            return False
        name_on_page = self.wait_for_text(self.EMPLOYEE_NAME)
        self.log.info("Employee created: %s", name_on_page)
        return expected_name.lower() in name_on_page.lower()

    def get_employee_number(self):
        """Read the internal empNumber from the URL (different from Employee Id)."""
        url = self.driver.current_url
        if "/empNumber/" not in url:
            return None
        return url.split("/empNumber/")[1].split("/")[0]
