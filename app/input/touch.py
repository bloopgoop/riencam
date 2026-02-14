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

        # Use calibrated values from your testing
        # Top-left was X=190, Y=3950
        # Bottom-right was X=3850, Y=200
        self.min_x = 190
        self.max_x = 3850
        self.min_y = 200   # Note: Y is inverted, so min is actually at bottom
        self.max_y = 3950

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _current_coords(self):
        # Normalize raw values to 0..1, clamping to valid range
        nx = max(0.0, min(1.0, (self.abs_x - self.min_x) / (self.max_x - self.min_x)))
        ny = max(0.0, min(1.0, (self.abs_y - self.min_y) / (self.max_y - self.min_y)))

        # For 90° rotation with your measured behavior:
        # - raw Y (inverted) maps to screen X
        # - raw X maps to screen Y
        screen_x = int((1.0 - ny) * self.screen_width)
        screen_y = int(nx * self.screen_height)

        # Safety clamp (should not be needed with the clamps above, but just in case)
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))

        print(screen_x, screen_y)

        return screen_x, screen_y

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