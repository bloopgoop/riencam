from views.base import BaseView, Devices
from views.overlay import TextButton
from font import draw_text
from framebuffer import rgb565


class CameraView(BaseView):

    def __init__(self, devices: Devices):
        self.devices = devices
        self.overlays = [
            TextButton(
                x=10,
                y=0,
                w=108,
                h=36,
                label="CAMERA",
                type="TOUCH",
                action="RELEASE",
                callback=None
            )
        ]
        self.render()

    def get_overlays(self):
        return self.overlays

    def render(self):
        self.devices.display.clear(rgb565(0, 0, 0))

        last = self.devices.camera.get_last_photo()
        if last:
            self.devices.display.draw_image(last)
        else:
            draw_text(self.devices.display, 40, 140, "READY", rgb565(255, 255, 255))

        for overlay in self.overlays:
            overlay.draw(self.devices.display)

    def handle_input(self, event) -> dict[str, str]:
        if event.type == "BUTTON" and event.action == "PRESS":
            print("Button press detected")
            path = self.devices.camera.capture()
            self.render()
            return {"status": "ok"}

        for overlay in self.overlays:
            if overlay.accepts_event(event):
                print("overylay", overlay.label, "accepts", event.type, event.action)
                if overlay.callback != None:
                    print(overlay.handle_event())
                    return overlay.handle_event()

        return {"status": "ok"}

    def on_enter(self):
        # Implement the method, even if it's empty
        pass

    def on_exit(self):
        # Implement the method, even if it's empty
        pass
