"""PIM > Employee List - search, verify and delete."""

import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config import Config


class EmployeeListPage(BasePage):

    EMPLOYEE_ID_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Employee Id']"
        "/ancestor::div[contains(@class,'oxd-input-group')]//input",
    )
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    RESULT_ROWS = (By.CSS_SELECTOR, "div.oxd-table-card")
    ROW_CELLS = (By.CSS_SELECTOR, "div.oxd-table-cell")
    HEADER_CELLS = (By.CSS_SELECTOR, "div.oxd-table-header-cell")
    NO_RECORDS = (By.XPATH, "//span[normalize-space()='No Records Found']")
    DELETE_ICON = (By.CSS_SELECTOR, "div.oxd-table-card button i.bi-trash")
    CONFIRM_DELETE = (By.XPATH, "//button[normalize-space()='Yes, Delete']")

    # Grid column heading -> key used in the tests
    COLUMN_KEYS = {
        "id": "id",
        "first (& middle) name": "first_middle_name",
        "last name": "last_name",
        "job title": "job_title",
        "employment status": "employment_status",
        "sub unit": "sub_unit",
        "supervisor": "supervisor",
    }

    def load(self):
        self.open(f"{Config.BASE_URL}/web/index.php/pim/viewEmployeeList")
        self.wait_for_loaders()
        return self

    def search_by_employee_id(self, employee_id):
        self.log.info("Search employee by Id '%s'", employee_id)
        self.close_toast()
        self.type_text(self.EMPLOYEE_ID_INPUT, employee_id)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_loaders()
        return self

    def _row_keys(self):
        """Read the column names from the grid header.
        The grid has an unnamed checkbox column first, so a fixed list of
        column names would not line up."""
        keys = []
        for index, header in enumerate(self.find_all(self.HEADER_CELLS)):
            label = header.text.strip().lower()
            keys.append(self.COLUMN_KEYS.get(label, label or f"column_{index}"))
        return keys or list(self.COLUMN_KEYS.values())

    def get_result_rows(self):
        """Return the visible rows as dictionaries."""
        for _ in range(3):
            try:
                keys = self._row_keys()
                rows = []
                for card in self.find_all(self.RESULT_ROWS):
                    cells = [cell.text.strip() for cell in card.find_elements(*self.ROW_CELLS)]
                    rows.append(dict(zip(keys, cells)))
                return rows
            except StaleElementReferenceException:
                self.log.debug("Grid reloaded while reading rows, trying again")
        raise StaleElementReferenceException("Could not read the employee grid")

    def _wait_for_row(self, employee_id, should_exist, timeout=15):
        """The grid fills in after the search response, so it is checked in a
        loop instead of once."""
        end_time = time.time() + timeout
        found = not should_exist
        while time.time() < end_time:
            if self.is_displayed(self.NO_RECORDS, timeout=1):
                found = False
                if not should_exist:
                    break
            found = any(row.get("id") == employee_id for row in self.get_result_rows())
            if found == should_exist:
                break
            time.sleep(0.4)
        self.log.info("Employee '%s' found in list: %s", employee_id, found)
        return found

    def is_employee_present(self, employee_id, timeout=15):
        return self._wait_for_row(employee_id, should_exist=True, timeout=timeout)

    def verify_employee_exists(self, employee_id):
        self.load().search_by_employee_id(employee_id)
        return self.is_employee_present(employee_id)

    def get_employee_row(self, employee_id):
        for row in self.get_result_rows():
            if row.get("id") == employee_id:
                return row
        raise AssertionError(f"No row found for Employee Id '{employee_id}'")

    def delete_employee(self, employee_id):
        if not self.is_employee_present(employee_id):
            raise AssertionError(f"Employee '{employee_id}' is not in the search results")
        self.log.info("Delete employee '%s'", employee_id)
        icons = self.find_all(self.DELETE_ICON)
        if not icons:
            raise AssertionError("Delete icon not found on the employee row")
        self.scroll_into_view(icons[0])
        self._show_step(icons[0])
        icons[0].click()
        self.confirm_delete()

    def confirm_delete(self):
        self.click(self.CONFIRM_DELETE)
        self.log.info("Delete message: %s", self.get_toast_message().replace("\n", " "))
        self.wait_for_loaders()
        self.close_toast()

    def verify_employee_not_present(self, employee_id):
        self.load().search_by_employee_id(employee_id)
        return not self._wait_for_row(employee_id, should_exist=False, timeout=10)
