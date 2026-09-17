"""Load the JSON test data and make the employee details unique."""

import json
import random
import string
from datetime import datetime

from utils.config import Config
from utils.logger import get_logger

log = get_logger("DataLoader")


def load_json(file_name="employee_data.json"):
    path = Config.DATA_DIR / file_name
    if not path.is_file():
        raise FileNotFoundError(f"Test data file not found: {path}")
    with path.open(encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {path}: {exc}")
    log.info("Test data loaded from %s", path.name)
    return data


def build_unique_employee(data):
    """Add a unique Employee Id and name to the data from JSON.

    The demo database is shared and never reset, so a fixed Employee Id would
    clash with an existing record. The field allows 10 characters, so the id is
    prefix (4) + minutes and seconds (4) + 2 random characters.
    """
    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    employee = dict(data)
    prefix = data.get("employee_id_prefix", "AUTO")[:4]
    employee["employee_id"] = f"{prefix}{stamp[-4:]}{random_part[:2]}"
    employee["first_name"] = f"{data['first_name']}{random_part}"
    employee["last_name"] = f"{data['last_name']}{stamp[-4:]}"

    log.info(
        "Employee for this run: %s (%s %s)",
        employee["employee_id"],
        employee["first_name"],
        employee["last_name"],
    )
    return employee


def resolve_profile_picture(relative_path):
    """Full path of the upload image. Creates it if the file is missing."""
    path = (Config.ROOT / relative_path).resolve()
    if path.is_file():
        return path

    log.warning("Profile picture missing at %s, creating one", path)
    path.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (200, 200), (26, 60, 110))
    draw = ImageDraw.Draw(image)
    draw.ellipse((70, 35, 130, 95), fill=(255, 255, 255))
    draw.ellipse((40, 105, 160, 220), fill=(255, 255, 255))
    image.save(path, format="PNG")
    return path
