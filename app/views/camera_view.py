from views.base import BaseView
from font import draw_text
from framebuffer import rgb565

class CameraView(BaseView):

    def on_enter(self):
        self.render()

    def render(self):
        self.fb.clear(rgb565(0, 0, 0))

        last = self.controller.camera.get_last_photo()
        if last:
            self.fb.draw_image(last)
        else:
            draw_text(self.fb, 40, 140, "READY", rgb565(255,255,255))

        self.draw_overlay()

    def draw_overlay(self):
        draw_text(self.fb, 10, 10, "CAMERA", rgb565(255,255,255))

    def handle_input(self, event):
        if event.type == "BUTTON" and event.action == "PRESS":
            print("Button press detected")
            path = self.controller.camera.capture()
            self.render()

        elif event.type == "TOUCH" and event.action == "PRESS":
            # placeholder: tap right side → gallery
            print("Touch press detected")
            if event.x and event.x > self.fb.width * 0.7:
                from views.gallery_view import GalleryView
                self.controller.switch_to(GalleryView)
