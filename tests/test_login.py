"""Login tests."""

import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config import Config


@pytest.mark.smoke
def test_login_with_valid_credentials(driver):
    login_page = LoginPage(driver).load()
    assert login_page.is_login_page_displayed(), "Login page did not load"

    login_page.login(Config.USERNAME, Config.PASSWORD)

    assert DashboardPage(driver).is_dashboard_displayed(), (
        "Dashboard was not displayed after login with valid credentials"
    )


@pytest.mark.smoke
def test_login_with_invalid_credentials(driver):
    """Negative test, so a passing login test does not simply mean the app
    accepts anyone."""
    login_page = LoginPage(driver).load()
    login_page.login(Config.USERNAME, "wrong-password")

    error = login_page.get_error_message()
    assert "invalid credentials" in error.lower(), (
        f"Expected the 'Invalid credentials' message, got '{error}'"
    )
    assert login_page.is_login_page_displayed(), "User was not kept on the login page"
