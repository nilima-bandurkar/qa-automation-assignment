"""PIM module navigation."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config import Config


class PIMPage(BasePage):

    MENU_PIM = (By.XPATH, "//aside//a[.//span[normalize-space()='PIM']]")
    ADD_EMPLOYEE_TAB = (By.XPATH, "//a[normalize-space()='Add Employee']")
    EMPLOYEE_LIST_TAB = (By.XPATH, "//a[normalize-space()='Employee List']")
    MODULE_HEADER = (By.CSS_SELECTOR, "h6.oxd-topbar-header-breadcrumb-module")

    def navigate_to_pim(self):
        self.log.info("Open PIM module")
        self.click(self.MENU_PIM)
        self.wait_for_url_contains("/pim/")
        self.wait_for_loaders()
        return self

    def click_add_employee(self):
        self.log.info("Open PIM > Add Employee")
        self.click(self.ADD_EMPLOYEE_TAB)
        self.wait_for_url_contains("/pim/addEmployee")

    def go_to_employee_list(self):
        self.log.info("Open PIM > Employee List")
        self.click(self.EMPLOYEE_LIST_TAB)
        self.wait_for_url_contains("/pim/viewEmployeeList")
        self.wait_for_loaders()

    def is_pim_displayed(self):
        return self.is_displayed(self.MODULE_HEADER) and "pim" in self.driver.current_url.lower()
