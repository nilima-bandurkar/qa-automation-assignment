"""Common Selenium helpers used by all page classes."""

import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import Config
from utils.logger import get_logger


class BasePage:
    """Waits, clicks, typing and dropdown handling for every page."""

    TOAST = (By.CSS_SELECTOR, "div.oxd-toast")
    SPINNER = (By.CSS_SELECTOR, ".oxd-loading-spinner")
    FORM_LOADER = (By.CSS_SELECTOR, "div.oxd-form-loader")

    def __init__(self, driver):
        self.driver = driver
        self.timeout = Config.EXPLICIT_WAIT
        self.log = get_logger(type(self).__name__)

    # ---------- waits ----------
    def _wait(self, timeout=None):
        return WebDriverWait(
            self.driver,
            timeout or self.timeout,
            poll_frequency=0.3,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def wait_for_visible(self, locator, timeout=None):
        return self._wait(timeout).until(
            EC.visibility_of_element_located(locator), f"Element not visible: {locator}"
        )

    def wait_for_present(self, locator, timeout=None):
        return self._wait(timeout).until(
            EC.presence_of_element_located(locator), f"Element not present: {locator}"
        )

    def wait_for_clickable(self, locator, timeout=None):
        return self._wait(timeout).until(
            EC.element_to_be_clickable(locator), f"Element not clickable: {locator}"
        )

    def wait_for_url_contains(self, part, timeout=None):
        return self._wait(timeout).until(
            EC.url_contains(part),
            f"URL never contained '{part}'. Current URL: {self.driver.current_url}",
        )

    def wait_for_text(self, locator, timeout=None):
        """Wait until the element actually shows text (it renders empty first)."""
        self._wait(timeout).until(
            lambda d: (d.find_element(*locator).text or "").strip() != "",
            f"Element has no text: {locator}",
        )
        return self.get_text(locator, timeout)

    def wait_for_loaders(self, timeout=15):
        """Wait for the spinner and form overlay to go away."""
        for locator in (self.SPINNER, self.FORM_LOADER):
            try:
                self._wait(timeout).until(EC.invisibility_of_element_located(locator))
            except TimeoutException:
                self.log.debug("Loader %s still visible, continuing", locator)

    # ---------- demo mode ----------
    def _show_step(self, element=None):
        """In demo mode, outline the element and pause so the step is visible."""
        if not Config.DEMO_MODE:
            return
        if element is not None:
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});"
                    "arguments[0].style.outline='3px solid #ff5722';",
                    element,
                )
            except Exception:
                return
        time.sleep(Config.STEP_DELAY)
        if element is not None:
            try:
                self.driver.execute_script("arguments[0].style.outline='';", element)
            except Exception:
                pass

    # ---------- actions ----------
    def open(self, url):
        self.log.info("Open %s", url)
        self.driver.get(url)

    def click(self, locator, timeout=None):
        """Click, retrying if the element re-renders or a toast covers it."""
        error = TimeoutException(f"Click failed: {locator}")
        for attempt in range(3):
            try:
                element = self.wait_for_clickable(locator, timeout)
                self._show_step(element)
                element.click()
                return
            except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
                error = exc
                self.log.debug("Click retry %s on %s", attempt + 1, locator)
                self.wait_for_loaders()
                self.close_toast()
        raise error

    def type_text(self, locator, value, timeout=None):
        """Clear the field properly, then type. Some fields refill themselves,
        so Ctrl+A + Delete is used and the value is checked afterwards."""
        error = TimeoutException(f"Typing failed: {locator}")
        for attempt in range(3):
            try:
                element = self.wait_for_visible(locator, timeout)
                self._show_step(element)
                element.click()
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(Keys.DELETE)
                element.clear()
                element.send_keys(value)

                current = element.get_attribute("value") or ""
                if current != value:
                    element.send_keys(Keys.END)
                    for _ in range(len(current) + len(value)):
                        element.send_keys(Keys.BACK_SPACE)
                    element.send_keys(value)
                return
            except (StaleElementReferenceException, ElementClickInterceptedException) as exc:
                error = exc
                self.log.debug("Typing retry %s on %s", attempt + 1, locator)
                self.wait_for_loaders()
                self.close_toast()
        raise error

    def get_text(self, locator, timeout=None):
        return self.wait_for_visible(locator, timeout).text.strip()

    def get_value(self, locator, timeout=None):
        return (self.wait_for_visible(locator, timeout).get_attribute("value") or "").strip()

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def is_displayed(self, locator, timeout=5):
        try:
            self.wait_for_visible(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

    # ---------- app components ----------
    def get_toast_message(self, timeout=10):
        """Text of the success/error message, or '' if it did not appear."""
        try:
            return self.wait_for_visible(self.TOAST, timeout).text.strip()
        except TimeoutException:
            return ""

    def close_toast(self):
        """Remove a toast so it cannot block the next click."""
        for toast in self.find_all(self.TOAST):
            try:
                self.driver.execute_script("arguments[0].remove();", toast)
            except StaleElementReferenceException:
                pass

    def select_from_dropdown(self, dropdown_locator, option_text):
        """OrangeHRM dropdowns are not <select>, options load after the click."""
        self.click(dropdown_locator)
        option = (By.XPATH, f"//div[@role='listbox']//span[normalize-space()=\"{option_text}\"]")
        try:
            element = self.wait_for_clickable(option)
            self._show_step(element)
            element.click()
        except TimeoutException:
            options = [o.text for o in self.find_all((By.CSS_SELECTOR, "div[role='option']"))]
            raise TimeoutException(
                f"Option '{option_text}' not found. Available options: {options}"
            )
