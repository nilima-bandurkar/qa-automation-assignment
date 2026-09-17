# Video recording

Selenium has no built-in video recorder. `utils/video_recorder.py` takes browser
screenshots on a background thread and joins them into an mp4 using OpenCV.

## How to enable it (Windows)

```cmd
pip install -r requirements-video.txt
set RECORD_VIDEO=true && pytest
```

Or set it permanently in `.env`:

```dotenv
RECORD_VIDEO=true
VIDEO_FPS=4
```

Videos are saved here as `<test name>_<timestamp>.mp4`, one file per test.

## What it can and cannot do

* Records the browser window only, not the whole desktop.
* Works in headless mode, which a screen recorder cannot do.
* Frame rate is low (4 per second by default) because every frame is a separate
  screenshot request.
* Native dialogs outside the page are not captured.

Recording is off by default so the normal run stays fast.

`test_run_employee_lifecycle.mp4` in this folder is a recording of an actual
full lifecycle run (login, add employee, search, edit, API check, delete,
logout).
