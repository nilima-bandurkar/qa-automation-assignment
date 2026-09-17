"""Create and configure the Chrome WebDriver."""

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.config import Config
from utils.logger import get_logger

log = get_logger("DriverFactory")


def _chrome_options():
    options = Options()
    if Config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Hides the automation info bar and the password save popup, which can
    # cover the buttons the test needs to click.
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option(
        "prefs",
        {"credentials_enable_service": False, "profile.password_manager_enabled": False},
    )
    # Lets the test read browser console errors when something fails.
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    chrome_path = os.getenv("CHROME_BINARY", "").strip()
    if chrome_path:
        options.binary_location = chrome_path
    return options


def create_driver():
    if Config.BROWSER != "chrome":
        raise ValueError(f"BROWSER='{Config.BROWSER}' is not supported. This project uses Chrome.")

    log.info("Starting Chrome (headless=%s)", Config.HEADLESS)
    driver = webdriver.Chrome(options=_chrome_options())
    # Implicit wait is kept at 0 because the project uses explicit waits only.
    driver.implicitly_wait(0)
    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    if not Config.HEADLESS:
        driver.maximize_window()
    return driver


def get_browser_errors(driver):
    """Console errors from the browser, useful when a test fails."""
    try:
        entries = driver.get_log("browser")
    except Exception:
        return []
    return [entry["message"] for entry in entries if entry.get("level") == "SEVERE"]
