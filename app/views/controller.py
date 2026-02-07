from base import BaseView


class ViewController:
    def __init__(self, current_view: BaseView | None, devices):
        self.devices = devices
        self.current_view: BaseView | None = current_view

    def switch_to(self, View):
        if not self.current_view:
            self.current_view = View(self.devices)

    def handle_input(self, event):
        if self.current_view:
            self.current_view.handle_input(event)
