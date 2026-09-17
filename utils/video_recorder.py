"""Optional video recording of the test run.

Selenium cannot record video by itself. This class takes browser screenshots
on a background thread and joins them into an mp4 using OpenCV. It records the
browser window only, and it works in headless mode too.
"""

import threading
import time
from datetime import datetime

from selenium.common.exceptions import WebDriverException

from utils.config import Config
from utils.logger import get_logger

log = get_logger("VideoRecorder")


class VideoRecorder:

    def __init__(self, driver, test_name):
        self.driver = driver
        self.test_name = test_name
        self.frames = []
        self.stop_flag = threading.Event()
        self.thread = None
        self.interval = 1.0 / max(Config.VIDEO_FPS, 1)

    def start(self):
        if not Config.RECORD_VIDEO:
            return
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()
        log.info("Recording started for '%s'", self.test_name)

    def _capture(self):
        while not self.stop_flag.is_set():
            try:
                self.frames.append(self.driver.get_screenshot_as_png())
            except WebDriverException:
                pass  # page is navigating or the browser is closing
            time.sleep(self.interval)

    def stop(self):
        if not Config.RECORD_VIDEO or self.thread is None:
            return None
        self.stop_flag.set()
        self.thread.join(timeout=10)
        if not self.frames:
            log.warning("No frames captured, video not created")
            return None
        return self._write_video()

    def _write_video(self):
        try:
            import cv2
            import numpy as np
        except ImportError:
            log.error("OpenCV is missing. Run: pip install -r requirements-video.txt")
            return None

        Config.ensure_directories()
        path = Config.VIDEO_DIR / f"{self.test_name}_{datetime.now():%Y%m%d_%H%M%S}.mp4"

        first_frame = cv2.imdecode(np.frombuffer(self.frames[0], np.uint8), cv2.IMREAD_COLOR)
        if first_frame is None:
            log.error("Could not read the first frame, video not created")
            return None
        height, width = first_frame.shape[:2]

        writer = cv2.VideoWriter(
            str(path), cv2.VideoWriter_fourcc(*"mp4v"), Config.VIDEO_FPS, (width, height)
        )
        try:
            for raw_frame in self.frames:
                frame = cv2.imdecode(np.frombuffer(raw_frame, np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                writer.write(frame)
        finally:
            writer.release()

        log.info("Video saved: %s (%s frames)", path, len(self.frames))
        return path
