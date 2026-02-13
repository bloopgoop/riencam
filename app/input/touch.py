import threading
from evdev import InputDevice, ecodes

from input.events import InputEvent


class Touchscreen:
    def __init__(self, device_path, screen_width, screen_height, rotation, callback):
        self.dev = InputDevice(device_path)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rotation = rotation
        self.callback = callback

        self.running = False
        self.thread = None

        self.abs_x = 0
        self.abs_y = 0
        self.touching = False

        absinfo_x = self.dev.absinfo(ecodes.ABS_X)
        absinfo_y = self.dev.absinfo(ecodes.ABS_Y)

        print(absinfo_x) # min 0, max 4095
        print(absinfo_y) # min 0, max 4095

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

    def _current_coords(self):
        # normalize raw values to 0..1
        nx = (self.abs_x - self.min_x) / (self.max_x - self.min_x)
        ny = (self.abs_y - self.min_y) / (self.max_y - self.min_y)

        # map axes based on measured behavior
        screen_x = 1.0 - ny   # raw_y → X, inverted
        screen_y = nx         # raw_x → Y

        # convert to pixels
        px = int(screen_x * (self.screen_width - 1))
        py = int(screen_y * (self.screen_height - 1))

        # safety clamp
        px = max(0, min(self.screen_width - 1, px))
        py = max(0, min(self.screen_height - 1, py))

        return px, py

    def _emit(self, action):
        x, y = self._current_coords()

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

            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                if event.value == 1 and not self.touching:
                    # finger down
                    self.touching = True
                    self._emit("PRESS")

                elif event.value == 0 and self.touching:
                    # finger up
                    self.touching = False
                    self._emit("RELEASE")
