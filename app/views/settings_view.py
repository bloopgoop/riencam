from views.base import BaseView, Devices
from views.overlay import TextButton
from font import draw_text
from framebuffer import rgb565



class Setting:
    def __init__(self, file_path="/etc/camera/settings.json"):
        # Default values
        self.brightness = 50
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                # Update attributes from the file
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")

    def save(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        data = {k: getattr(self, k) for k in self.__dict__ if k != "file_path"}
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)
        # Flush to disk
        with open(self.file_path, "r+") as f:
            f.flush()
            os.fsync(f.fileno())

class SettingsView(BaseView):

    def __init__(self, devices: Devices):
        self.devices = devices
        self.overlays = [
            TextButton(
                x=10,
                y=10,
                w=108,
                h=36,
                label="SETTINGS",
                type="TOUCH",
                action="PRESS",
                callback=None
            ),
        ]
        self.settings = Setting()
        self.render()

    def get_overlays(self):
        return self.overlays

    def render(self):
        self.devices.display.clear(rgb565(0, 0, 0))

        y = 60
        for i, s in enumerate(self.settings):
            color = rgb565(255,255,0) if i == self.index else rgb565(255,255,255)
            label = s.name if s.value is None else f"{s.name}: {s.value}"
            draw_text(self.devices.display, 40, y, label, color)
            y += 30

        draw_text(self.devices.display, 40, 10, "SETTINGS", rgb565(255,255,255))

        for overlay in self.overlays:
            overlay.draw(self.devices.display)

    def on_enter(self):
        self.settings = self._build_settings()
        self.index = 0
        self.render()

    def _build_settings(self):
        cam = self.devices.camera

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

    def handle_input(self, event):
        if event.type == "BUTTON" and event.action == "PRESS":
            return {"status": "ok"}

        for overlay in self.overlays:
            if overlay.accepts_event(event):
                print("overylay", overlay.label, "accepts", event.type, event.action)
                if overlay.callback != None:
                    print(overlay.handle_event())
                    return overlay.handle_event()
                
        return {"status": "ok"}

    def move_up(self):
        self.index = max(0, self.index - 1)
        self.render()

    def move_down(self):
        self.index = min(len(self.settings)-1, self.index + 1)
        self.render()

    def on_enter(self):
        # Implement the method, even if it's empty
        pass

    def on_exit(self):
        # Implement the method, even if it's empty
        pass
