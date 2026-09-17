"""Dashboard page shown after a successful login."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class DashboardPage(BasePage):

    HEADER = (By.CSS_SELECTOR, "h6.oxd-topbar-header-breadcrumb-module")
    DASHBOARD_GRID = (By.CSS_SELECTOR, ".orangehrm-dashboard-grid")
    USER_DROPDOWN = (By.CSS_SELECTOR, "span.oxd-userdropdown-tab")
    LOGOUT_LINK = (By.XPATH, "//a[normalize-space()='Logout']")

    def is_dashboard_displayed(self):
        """Check the URL, the page header and the dashboard widgets."""
        try:
            self.wait_for_url_contains("/dashboard/index")
        except Exception:
            return False
        if not self.is_displayed(self.HEADER):
            return False
        header = self.get_text(self.HEADER)
        self.log.info("Page header is '%s'", header)
        return header.lower() == "dashboard" and self.is_displayed(self.DASHBOARD_GRID)

    def logout(self):
        self.log.info("Logout")
        self.click(self.USER_DROPDOWN)
        self.click(self.LOGOUT_LINK)
        self.wait_for_url_contains("/auth/login")
