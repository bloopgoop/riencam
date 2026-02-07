from abc import ABC, abstractmethod
from framebuffer import Framebuffer
from camera import Camera

class Devices:
    def __init__(self, display: Framebuffer, camera: Camera):
        self.display = display
        self.camera = camera

class BaseView(ABC):
    @abstractmethod
    def __init__(self, devices):
        pass

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_exit(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def handle_input(self, event) -> dict[str, str]:
        pass
