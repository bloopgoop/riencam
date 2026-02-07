import os
from views.base import BaseView
from font import draw_text
from framebuffer import rgb565

class GalleryView(BaseView):

    def on_enter(self):
        self.images = self._load_images()
        self.index = len(self.images) - 1 if self.images else 0
        self.render()

    def _load_images(self):
        try:
            return sorted(
                os.path.join(self.controller.camera.PHOTO_DIR, f)
                for f in os.listdir(self.controller.camera.PHOTO_DIR)
                if f.endswith(".jpg")
            )
        except Exception:
            return []

    def render(self):
        self.fb.clear(rgb565(0, 0, 0))

        if not self.images:
            draw_text(self.fb, 40, 140, "NO IMAGES", rgb565(255,255,255))
            return

        self.fb.draw_image(self.images[self.index])
        self._draw_overlay()

    def _draw_overlay(self):
        label = f"{self.index+1}/{len(self.images)}"
        draw_text(self.fb, 10, 10, label, rgb565(255,255,255))

    def handle_input(self, event):
        if not self.images:
            return

        if event.type == "BUTTON" and event.action == "PRESS":
            self.next_image()

        elif event.type == "TOUCH" and event.action == "PRESS":
            if event.x < self.fb.width * 0.2:
                from views.camera_view import CameraView
                self.controller.switch_to(CameraView)
            elif event.x > self.fb.width * 0.8:
                self.next_image()
            else:
                self.prev_image()

    def next_image(self):
        self.index = (self.index + 1) % len(self.images)
        self.render()

    def prev_image(self):
        self.index = (self.index - 1) % len(self.images)
        self.render()
