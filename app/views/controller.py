from views.base import BaseView
from views.overlay import OverlayElement
from typing import List

class ViewController:
    def __init__(self, current_view: BaseView | None, devices, prehandlers: List[OverlayElement]):
        self.devices = devices
        self.current_view: BaseView | None = current_view
        self.prehandlers = prehandlers
        self.handlers = self.prehandlers.copy()

    def switch_to(self, View):
        print("Switching to", View)
        self.current_view = View(self.devices)
        view_handlers = self.current_view.get_overlays()
        self.handlers += self.prehandlers + view_handlers

    def handle_input(self, event):
        if self.current_view:
            return self.current_view.handle_input(event)
