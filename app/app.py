#!/usr/bin/env python3

import os
import time
import traceback

from framebuffer import Framebuffer
from camera import Camera

from views.controller import ViewController
from views.camera_view import CameraView
from views.gallery_view import GalleryView
from views.settings_view import SettingsView
from views.overlay import Button
from input.touch import Touchscreen
from input.events import InputEvent, LogEvent, RedirectEvent
from views.base import Devices

import RPi.GPIO as GPIO

from queue import Queue
import threading

event_queue = Queue()

SHUTTER_GPIO = 16

def shutter_thread(enqueue):
    # accept events from shutter
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(
        SHUTTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP  # idle HIGH, pressed LOW
    )

    last_state = GPIO.input(SHUTTER_GPIO)

    print("shutter damoen started from print")
    enqueue(LogEvent("INFO", "shutter daemon started"))
    enqueue(LogEvent("INFO", f"last state: {last_state}"))
    while True:
        current_state = GPIO.input(SHUTTER_GPIO)

        if last_state == GPIO.HIGH and current_state == GPIO.LOW:
            enqueue(LogEvent("INFO", "shutter event queued"))
            enqueue(InputEvent(type="BUTTON", action="PRESS"))

        last_state = current_state
        time.sleep(0.01)


def enqueue(event):
    event_queue.put(event)


# TO DO: figure out how to choose correct fb. This is a workaround for now. Sometimes uses existing fb0
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

    dirname = os.path.dirname(__file__)

    buttons = [
        Button(
            x=400, 
            y=10 + 64 * 1, 
            icon_w=36, 
            icon_h=36,
            button_w=48,
            button_h=48,
            path=os.path.join(dirname, "assets/camera-48.png"), 
            callback=lambda: controller.switch_to(CameraView),
            label="CAMERA",
            type="TOUCH",
            action="PRESS"
            ),
        Button(
            x=400, 
            y=10 + 64 * 2, 
            icon_w=36,
            icon_h=36,
            button_w=48,
            button_h=48,
            path=os.path.join(dirname, "assets/gallery-48.png"), 
            callback=lambda: controller.switch_to(GalleryView),
            label="GALLERY",
            type="TOUCH",
            action="PRESS"
            ),
        # Button(
        #     x=400, 
        #     y=10 + 64 * 3, 
        #     w=48, 
        #     h=48, 
        #     path=os.path.join(dirname, "assets/settings-48.png"), 
        #     callback=lambda: controller.switch_to(SettingsView),
        #     label="SETTINGS",
        #     type="TOUCH",
        #     action="PRESS"
        #     )
    ]


    # main controller
    controller = ViewController(current_view=None, devices=devices, prehandlers = buttons)
    controller.switch_to(CameraView)

    # accept events from touchscreen
    touch = Touchscreen(
        device_path="/dev/input/event0",
        screen_width=480,
        screen_height=320,
        rotation=90,
        callback=enqueue,
    )
    touch.start()

    # accept events from shutter
    threading.Thread(target=shutter_thread, args=(enqueue,), daemon=True).start()



    # main loop
    try:
        while True:
            event = event_queue.get()
            if (event == None):
                continue

            match event.type:
                case "LOG":
                    print(event.message)
    
                case _:
                    for handler in controller.handlers:
                        if handler.accepts_event(event):
                            handler.handle_event()
                            break
            
            # draw overlays
            for btn in buttons:
                btn.draw(framebuffer)

    except Exception as e:
        print(f"ERROR {e}")
        traceback.print_exc()
        time.sleep(2)

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
