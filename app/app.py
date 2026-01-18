#!/usr/bin/env python3

import os
import time
import subprocess
import datetime

from framebuffer import Framebuffer, rgb565
from font import draw_text

PHOTO_DIR = "/data/photos"
TEMP_FILE = os.path.join(PHOTO_DIR, ".capture.tmp")
CAPTURE_CMD = [
    "rpicam-still",
    "-n",                 # no preview
    "-t", "1",            # minimal delay
    "-o", TEMP_FILE
]

FB_DEV = "/dev/fb1"
CONFIG_FILE = "/etc/camera/camera.conf"
FB_WIDTH = 480
FB_HEIGHT = 320

def show_status(fb, text, bg_color):
    fb.clear(bg_color)
    draw_text(fb, 40, 140, text, rgb565(255, 255, 255))

def init_ui(fb_path):
    fb = Framebuffer(fb_path, FB_WIDTH, FB_HEIGHT)
    show_status(fb, "READY", rgb565(0, 128, 0))
    return fb

def ensure_dirs():
    os.makedirs(PHOTO_DIR, exist_ok=True)

def generate_filename():
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(PHOTO_DIR, f"{ts}.jpg")

def capture_image():
    final_path = generate_filename()

    # Run capture
    result = subprocess.run(CAPTURE_CMD)
    if result.returncode != 0:
        raise RuntimeError("Camera capture failed")

    # Flush to disk
    with open(TEMP_FILE, "rb") as f:
        os.fsync(f.fileno())

    # Atomic rename
    os.rename(TEMP_FILE, final_path)

    # Sync directory metadata
    dir_fd = os.open(PHOTO_DIR, os.O_DIRECTORY)
    os.fsync(dir_fd)
    os.close(dir_fd)

    return final_path

def main():
    ensure_dirs()
    fb = init_ui(FB_DEV)
    print("READY")

    # TEMP: auto-capture every 10 seconds for testing
    while True:
        time.sleep(10)
        try:
            show_status(fb, "CAPTURING", rgb565(128, 128, 0))
            path = capture_image()
            print(f"SAVED {path}")
            show_status(fb, "SAVED", rgb565(0, 0, 128))
        except Exception as e:
            print(f"ERROR {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
