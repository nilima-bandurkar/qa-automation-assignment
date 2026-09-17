"""End to end employee lifecycle test.

Login -> Add Employee -> Search -> Edit -> API check -> Delete -> API check -> Logout

It is one test because each step needs the employee created in the previous
step (the Employee Id and the internal empNumber are passed along).
"""

import pytest

from api.validators import assert_employee_data_matches
from pages.add_employee_page import AddEmployeePage
from pages.dashboard_page import DashboardPage
from pages.employee_details_page import EmployeeDetailsPage
from pages.employee_list_page import EmployeeListPage
from pages.login_page import LoginPage
from pages.pim_page import PIMPage
from utils.config import Config
from utils.logger import get_logger

log = get_logger("LifecycleTest")


@pytest.mark.e2e
def test_employee_lifecycle(logged_in_driver, employee_api, employee_data, profile_picture):
    driver = logged_in_driver
    api_client, is_orangehrm_api = employee_api

    employee_id = employee_data["employee_id"]
    first_name = employee_data["first_name"]
    last_name = employee_data["last_name"]
    expected_job_title = employee_data["job_title"]
    expected_status = employee_data["employment_status"]
    full_name = f"{first_name} {last_name}"

    # Step 1 - login (done by the fixture) and check the dashboard
    dashboard = DashboardPage(driver)
    assert dashboard.is_dashboard_displayed(), "Dashboard was not displayed after login"

    # Step 2 - add a new employee using the JSON data
    pim = PIMPage(driver)
    pim.navigate_to_pim()
    assert pim.is_pim_displayed(), "PIM module did not open"
    pim.click_add_employee()

    add_employee = AddEmployeePage(driver)
    assert add_employee.is_loaded(), "Add Employee form did not load"

    add_employee.enter_first_name(first_name)
    add_employee.enter_last_name(last_name)
    add_employee.enter_employee_id(employee_id)
    add_employee.upload_profile_picture(profile_picture)
    add_employee.save_employee()

    assert add_employee.verify_employee_created(full_name), (
        f"Employee '{full_name}' was not created - the employee page did not open after save"
    )
    emp_number = add_employee.get_employee_number()
    assert emp_number, f"Could not read empNumber from the URL for employee '{employee_id}'"
    log.info("Employee created: %s (empNumber=%s)", employee_id, emp_number)

    # Check the uploaded photo was really saved, not just previewed
    if is_orangehrm_api:
        photo = api_client.get_profile_picture(emp_number)
        assert len(photo) > 100, f"Profile picture was not saved (only {len(photo)} bytes)"
        log.info("Profile picture saved (%s bytes)", len(photo))

    # Step 3 - search the employee by Employee Id
    employee_list = EmployeeListPage(driver)
    assert employee_list.verify_employee_exists(employee_id), (
        f"Employee '{employee_id}' was not found in the employee list after creation"
    )

    # Step 4 - update Job Title and Employment Status
    details = EmployeeDetailsPage(driver)
    details.open_job_details(emp_number)
    details.update_job_title(expected_job_title)
    details.update_employment_status(expected_status)
    details.save_changes()

    # Read the values again after a page reload, so the check proves they saved
    ui_details = details.reload_job_details(emp_number)
    assert ui_details["job_title"] == expected_job_title, (
        f"Job Title not updated. Expected '{expected_job_title}', "
        f"page shows '{ui_details['job_title']}'"
    )
    assert ui_details["employment_status"] == expected_status, (
        f"Employment Status not updated. Expected '{expected_status}', "
        f"page shows '{ui_details['employment_status']}'"
    )

    # Step 5 - compare the UI data with the API data
    employee_list.load().search_by_employee_id(employee_id)
    assert employee_list.is_employee_present(employee_id), (
        f"Employee '{employee_id}' is missing from the list after the update"
    )
    row = employee_list.get_employee_row(employee_id)
    ui_data = {
        "employee_id": row["id"],
        "first_name": row["first_middle_name"],
        "last_name": row["last_name"],
        "job_title": row["job_title"],
        "employment_status": row["employment_status"],
    }
    log.info("Data read from the employee list: %s", ui_data)

    assert row["job_title"] == ui_details["job_title"], (
        f"Employee list shows Job Title '{row['job_title']}' but the Job tab "
        f"shows '{ui_details['job_title']}'"
    )

    if is_orangehrm_api:
        api_data = api_client.get_employee_snapshot(employee_id)
        assert api_data is not None, (
            f"API returned no employee for Employee Id '{employee_id}', but the UI shows it"
        )
        assert_employee_data_matches(ui_data, api_data)
        log.info("UI data matches the OrangeHRM API data")
    else:
        # Public test API: exercise the API layer but do not claim OrangeHRM
        # data was validated.
        response = api_client.create_employee(ui_data)
        assert response.get("employee_id") == employee_id, (
            "Fallback API did not return the employee_id that was sent"
        )
        log.warning("Public test API used - OrangeHRM data was NOT validated")

    # Step 6 - delete the employee from the UI
    employee_list.load().search_by_employee_id(employee_id)
    employee_list.delete_employee(employee_id)
    assert employee_list.verify_employee_not_present(employee_id), (
        f"Employee {employee_id} is still in the list after deletion"
    )

    # Step 7 - confirm the deletion through the API
    if is_orangehrm_api:
        assert not api_client.employee_exists(employee_id), (
            f"API still returns employee '{employee_id}' after the UI deleted it"
        )
        log.info("API confirms the employee is deleted")
    else:
        log.warning("Deletion could not be checked by API - see README")

    # Step 8 - logout and confirm the session is closed
    dashboard.logout()
    login_page = LoginPage(driver)
    assert login_page.is_login_page_displayed(), "Login page was not shown after logout"

    driver.get(Config.dashboard_url())
    login_page.wait_for_url_contains("/auth/login")
    assert login_page.is_login_page_displayed(), (
        "Dashboard was still open after logout - the session was not closed"
    )
    log.info("Lifecycle finished for employee %s", employee_id)
