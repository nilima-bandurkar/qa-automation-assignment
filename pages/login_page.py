"""Login page."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.config import Config


class LoginPage(BasePage):

    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    BRANDING = (By.CSS_SELECTOR, ".orangehrm-login-branding")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div[role='alert'] .oxd-alert-content-text")

    def load(self):
        self.open(Config.login_url())
        return self

    def enter_username(self, username):
        self.type_text(self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password):
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username, password):
        self.log.info("Login attempt with user '%s'", username)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def is_login_page_displayed(self):
        return self.is_displayed(self.USERNAME_INPUT) and self.is_displayed(self.BRANDING)

    def get_error_message(self):
        if self.is_displayed(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
