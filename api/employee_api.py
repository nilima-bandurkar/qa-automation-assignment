"""OrangeHRM employee API client.

OrangeHRM 5.x is a single page application that calls its own REST endpoints
under /web/index.php/api/v2/. These are real OrangeHRM endpoints with real
data, so the tests use them for validation.

Two points to keep in mind:
  * they are the application's own endpoints, not a separately published API,
  * they use the login session cookie, not an API token, so this client copies
    the cookies from the browser that is already logged in.
"""

import requests

from api.base_client import ApiError, BaseApiClient
from utils.config import Config

PIM = "/web/index.php/api/v2/pim"


class OrangeHRMEmployeeAPI(BaseApiClient):

    def __init__(self, session):
        super().__init__(Config.BASE_URL, session=session)

    @classmethod
    def from_driver(cls, driver):
        """Build a client that uses the browser's logged-in session."""
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"))
        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Referer": Config.dashboard_url(),
            }
        )
        return cls(session)

    def is_available(self):
        """Check the API answers before the tests rely on it."""
        try:
            response = self.request("GET", f"{PIM}/employees", params={"limit": 1})
            return "data" in self.json_of(response)
        except ApiError as exc:
            self.log.warning("OrangeHRM API not available: %s", exc)
            return False

    def search_employees(self, employee_id):
        response = self.request(
            "GET",
            f"{PIM}/employees",
            params={
                "nameOrId": employee_id,
                "limit": 50,
                "offset": 0,
                "includeEmployees": "onlyCurrent",
            },
        )
        records = self.json_of(response).get("data") or []
        self.log.info("API returned %s record(s) for '%s'", len(records), employee_id)
        return records

    def get_employee(self, employee_id):
        for record in self.search_employees(employee_id):
            if str(record.get("employeeId", "")).strip() == employee_id:
                return record
        return None

    def get_job_details(self, emp_number):
        response = self.request("GET", f"{PIM}/employees/{emp_number}/job-details")
        return self.json_of(response).get("data") or {}

    def get_employee_snapshot(self, employee_id):
        """Employee data in the same shape as the UI data, for comparison."""
        record = self.get_employee(employee_id)
        if record is None:
            return None
        job = self.get_job_details(str(record["empNumber"]))
        return {
            "employee_id": str(record.get("employeeId", "")).strip(),
            "first_name": (record.get("firstName") or "").strip(),
            "last_name": (record.get("lastName") or "").strip(),
            "job_title": ((job.get("jobTitle") or {}).get("title") or "").strip(),
            "employment_status": ((job.get("empStatus") or {}).get("name") or "").strip(),
        }

    def employee_exists(self, employee_id):
        return self.get_employee(employee_id) is not None

    def get_profile_picture(self, emp_number):
        """Download the saved photo, to confirm the upload really worked."""
        response = self.request("GET", f"/web/index.php/pim/viewPhoto/empNumber/{emp_number}")
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ApiError(f"Photo endpoint returned '{content_type}' instead of an image")
        return response.content

    def delete_employee(self, emp_number):
        """Not used by the main test (deletion is done through the UI), but
        kept so the client covers full CRUD."""
        self.request("DELETE", f"{PIM}/employees", json={"ids": [int(emp_number)]})
        self.log.info("API delete sent for empNumber=%s", emp_number)
        return True
