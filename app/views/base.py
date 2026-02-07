class BaseView:
    def __init__(self, controller):
        self.controller = controller
        self.fb = controller.framebuffer

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def render(self):
        raise NotImplementedError

    def handle_input(self, event):
        pass
