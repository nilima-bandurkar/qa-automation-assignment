"""Backup API client using a public test API (ReqRes).

This is used only if the OrangeHRM API cannot be reached. ReqRes has no
OrangeHRM data, so when this client is active the test does not claim that
OrangeHRM was validated - it only keeps the API checks running and logs a
clear warning. Method names match OrangeHRMEmployeeAPI, so swapping clients is
easy.
"""

from api.base_client import ApiError, BaseApiClient
from utils.config import Config


class PublicFallbackAPI(BaseApiClient):

    IS_SIMULATION = True
    SOURCE = "Public test API (ReqRes) - not OrangeHRM data"

    def __init__(self):
        super().__init__(Config.FALLBACK_API_URL)
        self.session.headers.update({"Accept": "application/json"})
        if Config.FALLBACK_API_KEY:
            self.session.headers.update({"x-api-key": Config.FALLBACK_API_KEY})

    def is_available(self):
        try:
            self.request("GET", "/users", params={"page": 1})
            return True
        except ApiError as exc:
            self.log.error("Fallback API also not reachable: %s", exc)
            return False

    def create_employee(self, employee):
        payload = {
            "name": f"{employee['first_name']} {employee['last_name']}",
            "job": employee["job_title"],
            "employee_id": employee["employee_id"],
            "employment_status": employee["employment_status"],
        }
        body = self.json_of(self.request("POST", "/users", json=payload, expected_status=(201,)))
        for field in ("id", "createdAt"):
            if field not in body:
                raise ApiError(f"Response is missing '{field}': {body}")
        self.log.info("Fallback API created record id=%s", body["id"])
        return body

    def get_employee(self, record_id):
        response = self.request("GET", f"/users/{record_id}", expected_status=(200, 404))
        if response.status_code == 404:
            return None
        return self.json_of(response).get("data")

    def update_employee(self, record_id, job_title):
        return self.json_of(self.request("PUT", f"/users/{record_id}", json={"job": job_title}))

    def delete_employee(self, record_id):
        self.request("DELETE", f"/users/{record_id}", expected_status=(204,))
        self.log.info("Fallback API delete returned 204 for id=%s", record_id)
        return True
