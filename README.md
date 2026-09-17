# OrangeHRM UI Automation (Selenium + Python + Pytest)

Automated end-to-end test of the employee lifecycle on the OrangeHRM demo
application, with API validation, HTML reporting and screenshots on failure.

Built and tested on **Windows with Google Chrome**.

**Application under test:** https://opensource-demo.orangehrmlive.com/
(demo login: `Admin` / `admin123`)

**Test scenario:**

```
Login
  -> Add Employee (data from JSON + profile picture upload)
  -> Search Employee (by Employee Id)
  -> Edit Employee (Job Title, Employment Status)
  -> API check (compare UI values with API values)
  -> Delete Employee (from UI)
  -> API check (record is gone)
  -> Logout (and confirm the session is closed)
```

---

## 1. Setup instructions

Requirements: Python 3.11 or newer, Google Chrome, and an internet connection.
ChromeDriver is not needed separately - Selenium Manager downloads the matching
version automatically.

Open Command Prompt in the project folder and run:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

The `.env` file holds the URL, username and password, so no credentials are
written inside the test code. Real environment variables take priority over the
file, which is how the CI workflow passes values without a file.

Settings available in `.env`:

| Setting | Default | Meaning |
|---|---|---|
| `ORANGEHRM_URL` | demo site URL | Application under test |
| `ORANGEHRM_USERNAME` | `Admin` | Login user |
| `ORANGEHRM_PASSWORD` | `admin123` | Login password |
| `BROWSER` | `chrome` | Browser to use |
| `HEADLESS` | `false` | `true` runs without opening a browser window |
| `DEMO_MODE` | `true` | Highlights each element and pauses, so every step is visible |
| `STEP_DELAY` | `0.5` | Pause in seconds used by demo mode |
| `EXPLICIT_WAIT` | `20` | Wait timeout in seconds |
| `RECORD_VIDEO` | `false` | Optional video recording |

## 2. Framework structure

```
orangehrm-selenium-python-automation\
|-- api\
|   |-- base_client.py          requests wrapper: timeout, status check, logging
|   |-- employee_api.py         OrangeHRM employee API calls
|   |-- fallback_api.py         backup public test API (only if OrangeHRM API fails)
|   |-- validators.py           compares UI data with API data
|-- data\
|   |-- employee_data.json      test data for the new employee
|-- pages\                      Page Object Model, one file per page
|   |-- base_page.py            waits, click, type, dropdowns, demo mode
|   |-- login_page.py
|   |-- dashboard_page.py
|   |-- pim_page.py
|   |-- add_employee_page.py
|   |-- employee_details_page.py
|   |-- employee_list_page.py
|-- reports\                    report, log and screenshots
|-- test_data\profile.png       image used for the upload
|-- tests\
|   |-- test_employee_lifecycle.py   full end-to-end scenario
|   |-- test_login.py                valid and invalid login
|   |-- test_api_layer.py            API reachability check
|-- utils\
|   |-- config.py               reads settings from .env
|   |-- driver_factory.py       Chrome setup
|   |-- data_loader.py          JSON loading + unique Employee Id
|   |-- logger.py               console and file logging
|   |-- screenshot.py           screenshot on failure
|   |-- video_recorder.py       optional video recording
|-- videos\
|-- conftest.py                 fixtures and failure reporting
|-- pytest.ini                  pytest settings and markers
|-- requirements.txt
|-- .env.example
```

How the layers work together:

* **Page Object Model** - each page has its own class holding its locators and
  its actions. Tests call methods like `add_employee.enter_employee_id(...)`, so
  no XPath is written inside a test file. If a locator changes, only one file
  changes.
* **Fixtures** (`conftest.py`) - `driver` starts a fresh browser for each test,
  `logged_in_driver` gives a browser that is already logged in, `employee_data`
  and `profile_picture` provide the test data, and `employee_api` returns the API
  client plus a flag saying whether it is the real OrangeHRM API.
* **Test data** - `data\employee_data.json` holds the employee details, and
  `utils\data_loader.py` makes the Employee Id and name unique for each run:
  `AUTO + minutes/seconds + 2 random characters` (10 characters, the field limit).
  The demo database is shared and never reset, so a fixed Employee Id would clash
  with an existing record.
* **Locators** - `id` and `name` are used where the app provides them
  (`username`, `password`, `firstName`, `lastName`). Fields with no id or name,
  such as Employee Id and the dropdowns, are found through their visible label,
  which is more stable than a fixed path.
* **Waits** - explicit waits only. Implicit wait is set to `0`, because mixing
  both wait types gives unpredictable timeouts. `base_page.py` has helpers for
  visible, clickable, present, URL change, text loaded, and loader disappeared.
* **API layer** - `api\employee_api.py` calls the OrangeHRM endpoints and returns
  the data in the same shape as the UI data, so `validators.py` can compare the
  two field by field.
* **Reporting** - failures produce a screenshot, browser console errors and a log
  entry, and every run creates an HTML report.

## 3. How to run the test

```cmd
pytest
```

That is all. The HTML report is created automatically because the options are
already set in `pytest.ini`.

Other useful commands:

```cmd
pytest -m smoke                             :: login tests only
pytest -m e2e                               :: full lifecycle test only
pytest -m api                               :: API test only
pytest tests\test_employee_lifecycle.py     :: run one file
set DEMO_MODE=false && pytest               :: faster run, no highlighting
set HEADLESS=true && pytest                 :: no browser window
```

**Demo mode:** `DEMO_MODE=true` is the default. Before every click or text entry
the element is scrolled into view, outlined in orange, and there is a short
pause, so each step is easy to follow in the browser. Speed is controlled by
`STEP_DELAY` in `.env`. Demo mode only adds the outline and the pause - all
waiting is still done with explicit waits, so the tests behave the same with
`DEMO_MODE=false`.

**Results after a run:**

| Output | Location |
|---|---|
| HTML report | `reports\report.html` |
| Execution log | `reports\test_execution.log` |
| Screenshots of failed tests | `reports\screenshots\` |
| Video (if enabled) | `videos\` |

A recording of an actual full run is already in the repository:
`videos\test_run_employee_lifecycle.mp4`.

Screenshots are named `<test name>_<timestamp>.png`, so nothing is overwritten,
and they are also linked inside the HTML report. The `reports\report.html` file
in this repository is from a real run against the live demo site.

## 4. Dependencies used

From `requirements.txt`:

| Package | Version | Why it is used |
|---|---|---|
| selenium | 4.25.0 | Browser automation. Selenium Manager downloads ChromeDriver automatically |
| pytest | 8.3.3 | Test runner, fixtures and markers |
| pytest-html | 4.1.1 | HTML test report |
| requests | 2.32.3 | API calls for the validation layer |
| python-dotenv | 1.0.1 | Reads settings and credentials from `.env` |
| Pillow | 10.4.0 | Creates the upload image if `test_data\profile.png` is missing |

Optional, only for video recording (`requirements-video.txt`):

| Package | Why it is used |
|---|---|
| opencv-python-headless | Joins the captured frames into an mp4 |
| numpy | Required by OpenCV |

Install them only if you want video:

```cmd
pip install -r requirements-video.txt
set RECORD_VIDEO=true && pytest
```

Videos are saved in `videos\` as `<test name>_<timestamp>.mp4`. The repository
already contains a recording of a real full run:
`videos\test_run_employee_lifecycle.mp4`. Details and limits are in
`videos\README.md`.

---

## API validation

The tests validate against the real OrangeHRM application data.

OrangeHRM 5.x is a single page application that calls its own REST endpoints
under `/web/index.php/api/v2/`. `api\employee_api.py` calls the same endpoints:

| Purpose | Endpoint |
|---|---|
| Find employee by Employee Id | `GET /api/v2/pim/employees?nameOrId=...` |
| Job title and employment status | `GET /api/v2/pim/employees/{empNumber}/job-details` |
| Saved profile photo | `GET /pim/viewPhoto/empNumber/{empNumber}` |
| Delete employee | `DELETE /api/v2/pim/employees` |

Two honest points about this:

1. These are the application's own endpoints. They are not a separately published
   API with a documented contract, so OrangeHRM does not guarantee they will stay
   the same.
2. They use the login session cookie instead of an API token, so the client
   copies the cookies from the browser that is already logged in
   (`OrangeHRMEmployeeAPI.from_driver`). This also means the API sees exactly the
   data the UI just created.

Before the checks run, `is_available()` calls the API once. If it cannot be
reached, the framework does not pretend the check happened:

* `api\fallback_api.py` uses a public test API (ReqRes) so the API code is still
  exercised - request building, headers, status codes and response checks;
* that API contains no OrangeHRM data and is never presented as OrangeHRM;
* in that case the lifecycle test skips the OrangeHRM data comparison and logs a
  warning, and `test_api_layer.py` is skipped with a reason;
* deletion also cannot be confirmed by API in that case, and the log says so.

Both clients use the same method names, so if a proper public OrangeHRM API is
available later, only the client created in `conftest.py` needs to change.

**UI and API comparison** (`api\validators.py`):

| Field | From UI | From API |
|---|---|---|
| Employee Id | employee list row | `employeeId` |
| First name | employee list row | `firstName` |
| Last name | employee list row | `lastName` |
| Job title | employee list row and Job tab | `jobTitle.title` |
| Employment status | employee list row and Job tab | `empStatus.name` |

The UI values are read back from the page after saving, not reused from the input
data, so the comparison is a real UI vs API check. All differences are reported
together in one failure message.

## Problems handled in the demo application

These came up while building the tests and are handled in the code:

1. **Employee Id field is pre-filled and limited to 10 characters**, and it
   refills itself, so `clear()` alone does not work. `type_text()` clears with
   Ctrl+A and Delete and then checks the value that ended up in the field.
2. **Job Title list is controlled by the admin** and has no "QA Automation
   Engineer" option, so the test uses "QA Engineer" from
   `data\employee_data.json`. If an option is missing, the error message lists
   the available options instead of just timing out.
3. **A form overlay covers the fields** for a moment after the page loads and
   blocks clicks, so the tests wait for it to disappear.
4. **The employee grid reloads** after a search, which breaks element references,
   so the rows are read again if that happens.
5. **The grid starts with an unnamed checkbox column**, so the column names are
   read from the grid header instead of using a fixed list.
6. **Employee Id is not shown on the Job tab**, so that value is read from the
   employee list page.
7. **The demo site is shared and never reset**, so each run creates its own
   employee and deletes it at the end.

`time.sleep()` is used in only three places, and never in place of a wait: the
`0.4` second gap inside the loop that polls the search grid, the frame interval
of the video recorder, and the demo mode pause.

## CI (GitHub Actions)

`.github\workflows\tests.yml` installs Python and Chrome, runs the tests in
headless mode and uploads the report, screenshots and log as artifacts.

One note: the OrangeHRM demo site is public and shared, so it is sometimes slow
or briefly down, and a CI run can fail for reasons that have nothing to do with
the tests. For blocking pull requests it is better to point `ORANGEHRM_URL` at a
private instance.

## Possible improvements

* Run in parallel with `pytest-xdist` (`pytest -n 4`). The design already allows
  it: the browser fixture is per test, every test creates its own Employee Id and
  no data is shared between tests.
* Add more employee records to the JSON file and run the same test for each one.
* Add cross-browser runs (Firefox, Edge) through Selenium Grid.
* Use a token-based API if OrangeHRM publishes one, and also create data through
  the API and verify it in the UI.
