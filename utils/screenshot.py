"""Save a screenshot when a test fails."""

import re
from datetime import datetime

from selenium.common.exceptions import WebDriverException

from utils.config import Config
from utils.logger import get_logger

log = get_logger("Screenshot")


def capture_screenshot(driver, test_name):
    """Save reports/screenshots/<test name>_<timestamp>.png."""
    Config.ensure_directories()
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", test_name)[:80]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Config.SCREENSHOT_DIR / f"{safe_name}_{timestamp}.png"
    try:
        driver.save_screenshot(str(path))
    except WebDriverException as exc:
        log.error("Screenshot failed for '%s': %s", test_name, exc)
        return None
    log.info("Screenshot saved: %s", path)
    return path
