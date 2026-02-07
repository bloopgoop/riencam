#!/usr/bin/env python3

import os
import time

from framebuffer import Framebuffer
from camera import Camera

from views.controller import ViewController
from views.camera_view import CameraView
from input.touch import Touchscreen
from input.events import InputEvent
from views.base import Devices

import RPi.GPIO as GPIO

from queue import Queue
import threading


event_queue = Queue()

SHUTTER_GPIO = 16

def shutter_thread(queue):
    # accept events from shutter
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(
        SHUTTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP  # idle HIGH, pressed LOW
    )

    last_state = GPIO.input(SHUTTER_GPIO)

    while True:
        current_state = GPIO.input(SHUTTER_GPIO)

        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            queue.put(InputEvent(type="BUTTON", action="PRESS"))

        last_state = current_state
        time.sleep(0.01)


def on_touch(event):
    event_queue.put(event)


def find_tft_framebuffer():
    while True:
        for fb in os.listdir("/sys/class/graphics"):
            try:
                with open(f"/sys/class/graphics/{fb}/name") as f:
                    name = f.read().lower()
                if "ili9486" in name or "tft" in name:
                    print(f"Found framebuffer: /dev/{fb}")
                    return f"/dev/{fb}"
            except IOError:
                pass
        time.sleep(0.05)


def main():
    # initialize
    fb_path = find_tft_framebuffer()
    print("READY")

    # intialize devices
    framebuffer = Framebuffer(fb_path=fb_path, width=480, height=320)
    camera = Camera(
        PHOTO_DIR="/data/photos",
        CONFIG_FILE="/etc/camera/camera.conf",
    )
    devices = Devices(display=framebuffer, camera=camera)

    # main controller
    controller = ViewController(current_view=None, devices=devices)
    controller.switch_to(CameraView)

    # accept events from touchscreen
    touch = Touchscreen(
        device_path="/dev/input/event0",
        screen_width=480,
        screen_height=320,
        callback=on_touch,
    )
    touch.start()

    # accept events from shutter
    threading.Thread(target=shutter_thread, args=(event_queue,), daemon=True)

    # main loop
    try:
        while True:
            event = event_queue.get()
            result = None
            if event:
                result = controller.handle_input(event)

            if result:
                if result["nextView"]:
                    event_queue.put(result["nextView"])

    except Exception as e:
        print(f"ERROR {e}")
        time.sleep(2)

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
