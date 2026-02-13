import os
import datetime
import subprocess

from font import draw_text
from framebuffer import Framebuffer, rgb565

class Camera:

    def __init__(self, PHOTO_DIR, CONFIG_FILE):
        self.PHOTO_DIR = PHOTO_DIR
        self.TEMP_FILE = os.path.join(PHOTO_DIR, ".capture.tmp")
        
        self.state = "STARTUP"

        self.jpeg_quality = 85
        self.resolution = "FULL"

        os.makedirs(self.PHOTO_DIR, exist_ok=True)

    def set_jpeg_quality(self, value):
        self.jpeg_quality = max(10, min(100, value))

    def capture(self):
        filepath = self.generate_filepath()

        # Run capture
        result = subprocess.run([
            "rpicam-still",
            "-n",
            "--width",
            "480",
            "--height",
            "320",
            "-o",
            self.TEMP_FILE
        ], check=True)
        if result.returncode != 0:
            raise RuntimeError("Camera capture failed")

        try:
            # Flush to disk
            with open(self.TEMP_FILE, "rb") as f:
                os.fsync(f.fileno())

            # Atomic rename
            os.rename(self.TEMP_FILE, filepath)

            # Sync directory metadata
            dir_fd = os.open(self.PHOTO_DIR, os.O_DIRECTORY)
            os.fsync(dir_fd)
            os.close(dir_fd)

        except Exception as e:
            raise RuntimeError("Save photo failed")

        return filepath

    # ----------- Utility Functions -----------

    def generate_filepath(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(self.PHOTO_DIR, f"{timestamp}.jpg")
    
    def get_last_photo(self):
        try:
            files = sorted(
                f for f in os.listdir(self.PHOTO_DIR)
                if f.endswith(".jpg")
            )
            if not files:
                return None
            return os.path.join(self.PHOTO_DIR, files[-1])
        except Exception:
            return None