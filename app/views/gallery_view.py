import os
from views.base import BaseView, Devices
from views.overlay import TextButton
from font import draw_text
from framebuffer import rgb565

class GalleryView(BaseView):

    def __init__(self, devices: Devices):
        self.devices = devices
        self.overlays = [
            TextButton(
                x=10,
                y=0,
                w=108,
                h=36,
                label="GALLERY",
                type="TOUCH",
                action="RELEASE",
                callback=None
            ),
            TextButton(
                x=10,
                y=140,
                w=108,
                h=36,
                label="BACK",
                type="TOUCH",
                action="RELEASE",
                callback=self.prev_image
            ),
            TextButton(
                x=380,
                y=140,
                w=108,
                h=36,
                label="NEXT",
                type="TOUCH",
                action="RELEASE",
                callback=self.next_image
            )
        ]
        self.images = self._load_images()
        self.index = len(self.images) - 1 if self.images else 0
        self.render()

    def get_overlays(self):
        return self.overlays

    def _load_images(self):
        try:
            return sorted(
                os.path.join(self.devices.camera.PHOTO_DIR, f)
                for f in os.listdir(self.devices.camera.PHOTO_DIR)
                if f.endswith(".jpg")
            )
        except Exception:
            return []

    def render(self):
        self.devices.display.clear(rgb565(0, 0, 0))

        if not self.images:
            draw_text(self.devices.display, 40, 140, "NO IMAGES", rgb565(255,255,255))
            return

        self.devices.display.draw_image(self.images[self.index])

        for overlay in self.overlays:
            overlay.draw(self.devices.display)

    def handle_input(self, event):
        if not self.images:
            return {"status":"404"}

        if event.type == "BUTTON" and event.action == "PRESS":
            self.next_image()
            return {"status": "ok"}
        

        for overlay in self.overlays:
            if overlay.accepts_event(event):
                print("overylay", overlay.label, "accepts", event.type, event.action)
                if overlay.callback != None:
                    print(overlay.handle_event())
                    return overlay.handle_event()
                
        return {"status": "ok"}


    def next_image(self):
        self.index = (self.index + 1) % len(self.images)
        self.render()

    def prev_image(self):
        self.index = (self.index - 1) % len(self.images)
        self.render()

    def on_enter(self):
        # Implement the method, even if it's empty
        pass

    def on_exit(self):
        # Implement the method, even if it's empty
        pass
