"""All settings come from environment variables / .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


def _bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes")


def _int(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _float(name, default):
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


class Config:
    """Runtime settings. Nothing is hard-coded in the tests."""

    # Application under test
    BASE_URL = os.getenv("ORANGEHRM_URL", "https://opensource-demo.orangehrmlive.com/").rstrip("/")
    USERNAME = os.getenv("ORANGEHRM_USERNAME", "Admin")
    PASSWORD = os.getenv("ORANGEHRM_PASSWORD", "admin123")

    # Browser
    BROWSER = os.getenv("BROWSER", "chrome").strip().lower()
    HEADLESS = _bool("HEADLESS")

    # Timeouts (seconds)
    EXPLICIT_WAIT = _int("EXPLICIT_WAIT", 20)
    PAGE_LOAD_TIMEOUT = _int("PAGE_LOAD_TIMEOUT", 45)
    API_TIMEOUT = _int("API_TIMEOUT", 30)

    # Demo mode: highlights each element and pauses so the run can be watched
    DEMO_MODE = _bool("DEMO_MODE", "true")
    STEP_DELAY = _float("STEP_DELAY", 0.5)

    # Video recording (needs requirements-video.txt)
    RECORD_VIDEO = _bool("RECORD_VIDEO")
    VIDEO_FPS = _int("VIDEO_FPS", 4)

    # Public test API, used only if the OrangeHRM API is unreachable
    FALLBACK_API_URL = os.getenv("FALLBACK_API_URL", "https://reqres.in/api").rstrip("/")
    FALLBACK_API_KEY = os.getenv("FALLBACK_API_KEY", "reqres-free-v1")

    # Folders
    ROOT = ROOT_DIR
    DATA_DIR = ROOT_DIR / "data"
    REPORTS_DIR = ROOT_DIR / "reports"
    SCREENSHOT_DIR = ROOT_DIR / "reports" / "screenshots"
    VIDEO_DIR = ROOT_DIR / "videos"
    LOG_FILE = ROOT_DIR / "reports" / "test_execution.log"

    @classmethod
    def ensure_directories(cls):
        for folder in (cls.REPORTS_DIR, cls.SCREENSHOT_DIR, cls.VIDEO_DIR):
            folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def login_url(cls):
        return f"{cls.BASE_URL}/web/index.php/auth/login"

    @classmethod
    def dashboard_url(cls):
        return f"{cls.BASE_URL}/web/index.php/dashboard/index"

    @classmethod
    def as_safe_dict(cls):
        """Settings for the report/log, with the password masked."""
        return {
            "base_url": cls.BASE_URL,
            "username": cls.USERNAME,
            "password": "********",
            "browser": cls.BROWSER,
            "headless": cls.HEADLESS,
            "explicit_wait": cls.EXPLICIT_WAIT,
            "demo_mode": cls.DEMO_MODE,
        }
