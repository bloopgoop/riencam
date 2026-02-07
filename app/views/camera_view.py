from views.base import BaseView, Devices
from font import draw_text
from framebuffer import rgb565


class CameraView(BaseView):

    def __init__(self, devices: Devices):
        self.devices = devices
        self.render()

    def render(self):
        self.devices.display.clear(rgb565(0, 0, 0))

        last = self.devices.camera.get_last_photo()
        if last:
            self.devices.display.draw_image(last)
        else:
            draw_text(self.devices.display, 40, 140, "READY", rgb565(255, 255, 255))

        self.draw_overlay()

    def draw_overlay(self):
        draw_text(self.devices.display, 10, 10, "CAMERA", rgb565(255, 255, 255))

    def handle_input(self, event) -> dict[str, str]:
        if event.type == "BUTTON" and event.action == "PRESS":
            print("Button press detected")
            path = self.devices.camera.capture()
            self.render()
            return {"status": "ok"}

        elif event.type == "TOUCH" and event.action == "PRESS":
            # placeholder: tap right side → gallery
            print("Touch press detected")
            if event.x and event.x > self.devices.display.width * 0.7:
                return {"nextView": "Gallery"}

        return {"status": "ok"}
