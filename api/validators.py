"""Compare employee data taken from the UI with data from the API."""

from utils.logger import get_logger

log = get_logger("Validators")

FIELDS = ("employee_id", "first_name", "last_name", "job_title", "employment_status")


def compare_employee_data(ui_data, api_data, fields=FIELDS):
    """Return a list of differences. An empty list means the data matches."""
    differences = []
    for field in fields:
        if field not in ui_data or field not in api_data:
            differences.append(f"{field}: missing on one side, cannot compare")
            continue
        ui_value = (ui_data[field] or "").strip()
        api_value = (api_data[field] or "").strip()
        if ui_value.lower() != api_value.lower():
            differences.append(f"{field}: UI='{ui_value}' API='{api_value}'")
        else:
            log.info("Match on %s = '%s'", field, ui_value)
    return differences


def assert_employee_data_matches(ui_data, api_data):
    differences = compare_employee_data(ui_data, api_data)
    assert not differences, "UI and API data do not match:\n  - " + "\n  - ".join(differences)
