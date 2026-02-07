import threading
from evdev import InputDevice, ecodes

from input.events import InputEvent

class Touchscreen:
    def __init__(self, device_path, screen_width, screen_height, callback):
        """
        device_path: /dev/input/eventX
        callback: function(InputEvent)
        """
        self.dev = InputDevice(device_path)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.callback = callback

        self.running = False
        self.thread = None

        self.abs_x = 0
        self.abs_y = 0
        self.touching = False

        # Read ABS ranges from device
        absinfo_x = self.dev.absinfo(ecodes.ABS_X)
        absinfo_y = self.dev.absinfo(ecodes.ABS_Y)

        self.min_x = absinfo_x.min
        self.max_x = absinfo_x.max
        self.min_y = absinfo_y.min
        self.max_y = absinfo_y.max

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _scale(self, value, min_v, max_v, out_max):
        return int((value - min_v) * out_max / (max_v - min_v))

    def _emit(self, action):
        x = self._scale(self.abs_x, self.min_x, self.max_x, self.screen_width)
        y = self._scale(self.abs_y, self.min_y, self.max_y, self.screen_height)

        # rotate 90 degrees
        x, y = y, self.screen_width - x

        self.callback(InputEvent(
            type="TOUCH",
            action=action,
            x=x,
            y=y
        ))

    def _run(self):
        for event in self.dev.read_loop():
            if not self.running:
                break

            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    self.abs_x = event.value
                elif event.code == ecodes.ABS_Y:
                    self.abs_y = event.value

                if self.touching:
                    self._emit("MOVE")

            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_TOUCH:
                    if event.value == 1:
                        self.touching = True
                        self._emit("PRESS")
                    else:
                        self.touching = False
                        self._emit("RELEASE")
