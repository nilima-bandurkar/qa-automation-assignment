"""Pytest fixtures: settings, browser setup/teardown and failure reporting."""

import pytest

from api.employee_api import OrangeHRMEmployeeAPI
from api.fallback_api import PublicFallbackAPI
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.config import Config
from utils.data_loader import build_unique_employee, load_json, resolve_profile_picture
from utils.driver_factory import create_driver, get_browser_errors
from utils.logger import configure_logging, get_logger
from utils.screenshot import capture_screenshot
from utils.video_recorder import VideoRecorder

log = get_logger("Fixtures")


@pytest.fixture(scope="session", autouse=True)
def test_setup():
    """Load the .env settings and create the output folders once per run."""
    configure_logging()
    Config.ensure_directories()
    log.info("Settings for this run: %s", Config.as_safe_dict())


@pytest.fixture(scope="session")
def employee_data():
    """Employee record from JSON, with a unique Employee Id for this run."""
    return build_unique_employee(load_json("employee_data.json"))


@pytest.fixture(scope="session")
def profile_picture(employee_data):
    return resolve_profile_picture(employee_data["profile_picture"])


@pytest.fixture
def driver(request):
    """A fresh browser for each test."""
    web_driver = create_driver()
    recorder = VideoRecorder(web_driver, request.node.name)
    recorder.start()

    request.node.driver = web_driver  # used by the failure hook below
    yield web_driver

    recorder.stop()
    log.info("Closing browser")
    web_driver.quit()


@pytest.fixture
def logged_in_driver(driver):
    """A browser that is already logged in, so other tests do not repeat it."""
    LoginPage(driver).load().login(Config.USERNAME, Config.PASSWORD)
    assert DashboardPage(driver).is_dashboard_displayed(), (
        "Login failed, so the test cannot start from a logged-in session"
    )
    log.info("Login successful")
    return driver


@pytest.fixture
def employee_api(logged_in_driver):
    """Return (client, is_orangehrm_api).

    The OrangeHRM API is checked first. If it cannot be reached, the public
    test API is used instead and the flag becomes False, so the test does not
    claim OrangeHRM data was validated.
    """
    client = OrangeHRMEmployeeAPI.from_driver(logged_in_driver)
    if client.is_available():
        log.info("Using the OrangeHRM employee API for validation")
        return client, True

    log.warning("OrangeHRM API not reachable. Using the public test API (no OrangeHRM data).")
    return PublicFallbackAPI(), False


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """On failure: save a screenshot and log browser console errors."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    web_driver = getattr(item, "driver", None)
    if web_driver is None:
        return

    screenshot = capture_screenshot(web_driver, item.name)
    for message in get_browser_errors(web_driver):
        log.error("Browser console: %s", message)

    if screenshot is None:
        return
    try:
        import pytest_html

        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.image(f"screenshots/{screenshot.name}", name="Screenshot"))
        report.extras = extras
    except Exception as exc:
        log.debug("Could not attach the screenshot to the report: %s", exc)


def pytest_configure(config):
    """Show the run settings in the HTML report (password is masked)."""
    Config.ensure_directories()
    try:
        from pytest_metadata.plugin import metadata_key

        config.stash[metadata_key].update(Config.as_safe_dict())
    except Exception as exc:
        log.debug("Could not add settings to the report: %s", exc)
