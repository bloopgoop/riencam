from views.base import BaseView
from font import draw_text
from framebuffer import rgb565

class Setting:
    def __init__(self, name, value, immediate, apply_fn=None):
        self.name = name
        self.value = value
        self.immediate = immediate
        self.apply_fn = apply_fn

class SettingsView(BaseView):

    def on_enter(self):
        self.settings = self._build_settings()
        self.index = 0
        self.render()

    def _build_settings(self):
        cam = self.controller.camera

        return [
            Setting(
                "JPEG QUALITY",
                cam.jpeg_quality,
                immediate=True,
                apply_fn=cam.set_jpeg_quality
            ),
            Setting(
                "RESOLUTION",
                cam.resolution,
                immediate=False
            ),
            Setting("BACK", None, immediate=True)
        ]

    def render(self):
        self.fb.clear(rgb565(0, 0, 0))

        y = 60
        for i, s in enumerate(self.settings):
            color = rgb565(255,255,0) if i == self.index else rgb565(255,255,255)
            label = s.name if s.value is None else f"{s.name}: {s.value}"
            draw_text(self.fb, 40, y, label, color)
            y += 30

        draw_text(self.fb, 40, 10, "SETTINGS", rgb565(255,255,255))

    def handle_input(self, event):
        if event.type == "BUTTON" and event.action == "PRESS":
            self.activate()

        elif event.type == "TOUCH" and event.action == "PRESS":
            if event.y < self.fb.height * 0.3:
                self.move_up()
            elif event.y > self.fb.height * 0.7:
                self.move_down()
            else:
                self.activate()

    def move_up(self):
        self.index = max(0, self.index - 1)
        self.render()

    def move_down(self):
        self.index = min(len(self.settings)-1, self.index + 1)
        self.render()

    def activate(self):
        s = self.settings[self.index]

        if s.name == "BACK":
            from views.camera_view import CameraView
            self.controller.switch_to(CameraView)
            return

        if isinstance(s.value, int):
            s.value += 5
        elif isinstance(s.value, str):
            s.value = "NEXT"  # placeholder

        if s.immediate and s.apply_fn:
            s.apply_fn(s.value)

        self.render()
