#!/usr/bin/env python3

import os
import time

from framebuffer import Framebuffer
from camera import Camera

from views.controller import ViewController
from views.camera_view import CameraView
from input.touch import Touchscreen
from input.events import InputEvent

import RPi.GPIO as GPIO

SHUTTER_GPIO = 36

def main():
    while not os.path.exists("/dev/fb1"):
        time.sleep(0.05)
    print("READY")

    framebuffer = Framebuffer(fb_path="/dev/fb1", width=480, height=320)
    camera = Camera(
        PHOTO_DIR="/data/photos", 
        CONFIG_FILE="/etc/camera/camera.conf", 
    )

    controller = ViewController(framebuffer=framebuffer, camera=camera)
    controller.switch_to(CameraView)

    touch = Touchscreen(
        device_path="/dev/input/event0",
        screen_width=480,
        screen_height=320,
        callback=controller.handle_input
    )
    touch.start()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(
        SHUTTER_GPIO,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP    # idle HIGH, pressed LOW
    )


    last_state = GPIO.input(SHUTTER_GPIO)
    print(f"starting button state: {last_state}")

    try:
        while True:
            current_state = GPIO.input(SHUTTER_GPIO)

            if last_state == GPIO.HIGH and current_state == GPIO.LOW:
                print("BUTTON PRESSED")
                controller.handle_input(
                    InputEvent(type="BUTTON", action="PRESS")
                )
                print(f"SAVED {path}")

            last_state = current_state
            time.sleep(0.01)  # 10 ms poll (fast enough for human input)

            # camera.show_status(bg_color=rgb565(0, 0, 128), text="SAVED")
    except Exception as e:
        print(f"ERROR {e}")
        time.sleep(2)

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
