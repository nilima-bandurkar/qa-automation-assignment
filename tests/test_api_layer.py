"""API layer test."""

import pytest


@pytest.mark.api
def test_employee_api_returns_employees(employee_api):
    """The API used for validation must return a list of employees.

    If the OrangeHRM API is not reachable, the test is skipped with a reason
    instead of passing against the public test API, which has no OrangeHRM data.
    """
    api_client, is_orangehrm_api = employee_api
    if not is_orangehrm_api:
        pytest.skip("OrangeHRM API not reachable, so this check would not mean anything")

    employees = api_client.search_employees("a")
    assert isinstance(employees, list), f"Expected a list of employees, got {type(employees)}"
