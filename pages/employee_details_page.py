"""Employee record - Job tab (job title and employment status)."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config import Config


class EmployeeDetailsPage(BasePage):

    JOB_TAB = (By.XPATH, "//a[contains(@href,'viewJobDetails')]")
    JOB_HEADER = (By.XPATH, "//h6[normalize-space()='Job Details']")
    SAVE_BUTTON = (By.CSS_SELECTOR, "form button[type='submit']")
    EMPLOYEE_NAME = (By.CSS_SELECTOR, ".orangehrm-edit-employee-name h6")

    JOB_TITLE_DROPDOWN = (
        By.XPATH,
        "//label[normalize-space()='Job Title']"
        "/ancestor::div[contains(@class,'oxd-input-group')]//div[contains(@class,'oxd-select-text')]",
    )
    JOB_TITLE_VALUE = (
        By.XPATH,
        "//label[normalize-space()='Job Title']"
        "/ancestor::div[contains(@class,'oxd-input-group')]"
        "//div[contains(@class,'oxd-select-text-input')]",
    )
    EMPLOYMENT_STATUS_DROPDOWN = (
        By.XPATH,
        "//label[normalize-space()='Employment Status']"
        "/ancestor::div[contains(@class,'oxd-input-group')]//div[contains(@class,'oxd-select-text')]",
    )
    EMPLOYMENT_STATUS_VALUE = (
        By.XPATH,
        "//label[normalize-space()='Employment Status']"
        "/ancestor::div[contains(@class,'oxd-input-group')]"
        "//div[contains(@class,'oxd-select-text-input')]",
    )

    def open_job_details(self, employee_number):
        self.open(f"{Config.BASE_URL}/web/index.php/pim/viewJobDetails/empNumber/{employee_number}")
        self.wait_for_visible(self.JOB_HEADER)
        self.wait_for_loaders()
        self.log.info("Job tab open for empNumber=%s", employee_number)
        return self

    def click_job_tab(self):
        self.click(self.JOB_TAB)
        self.wait_for_visible(self.JOB_HEADER)
        self.wait_for_loaders()
        return self

    def update_job_title(self, job_title):
        self.log.info("Set Job Title = '%s'", job_title)
        self.select_from_dropdown(self.JOB_TITLE_DROPDOWN, job_title)
        return self

    def update_employment_status(self, status):
        self.log.info("Set Employment Status = '%s'", status)
        self.select_from_dropdown(self.EMPLOYMENT_STATUS_DROPDOWN, status)
        return self

    def save_changes(self):
        self.click(self.SAVE_BUTTON)
        self.log.info("Job details saved. Message: %s", self.get_toast_message().replace("\n", " "))
        self.wait_for_loaders()
        self.close_toast()

    def get_employee_details(self):
        """Read the saved values from the page.
        Employee Id is not shown on this tab, so it is read from the list page."""
        details = {
            "job_title": self.wait_for_text(self.JOB_TITLE_VALUE),
            "employment_status": self.get_text(self.EMPLOYMENT_STATUS_VALUE),
            "full_name": self.wait_for_text(self.EMPLOYEE_NAME),
        }
        self.log.info("Values on page: %s", details)
        return details

    def reload_job_details(self, employee_number):
        """Reload the page first, so the values come from the server."""
        self.open_job_details(employee_number)
        return self.get_employee_details()
