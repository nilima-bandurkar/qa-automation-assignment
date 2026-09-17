"""Small wrapper over requests, shared by the API clients."""

import requests

from utils.config import Config
from utils.logger import get_logger


class ApiError(Exception):
    """Raised when a request fails or returns an unexpected status code."""


class BaseApiClient:

    def __init__(self, base_url, session=None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = Config.API_TIMEOUT
        self.log = get_logger(type(self).__name__)

    def request(self, method, path, expected_status=(200,), **kwargs):
        url = f"{self.base_url}{path}"
        self.log.info("API request: %s %s", method.upper(), url)
        try:
            response = self.session.request(method.upper(), url, timeout=self.timeout, **kwargs)
        except requests.Timeout:
            raise ApiError(f"{method.upper()} {url} timed out after {self.timeout}s")
        except requests.RequestException as exc:
            raise ApiError(f"{method.upper()} {url} failed: {exc}")

        self.log.info("API response: %s", response.status_code)
        if response.status_code not in expected_status:
            raise ApiError(
                f"{method.upper()} {url} returned {response.status_code}, "
                f"expected {list(expected_status)}. Response: {response.text[:300]}"
            )
        return response

    @staticmethod
    def json_of(response):
        try:
            data = response.json()
        except ValueError:
            raise ApiError(f"Response is not JSON: {response.text[:200]}")
        if not isinstance(data, dict):
            raise ApiError(f"Expected a JSON object, got {type(data)}")
        return data
