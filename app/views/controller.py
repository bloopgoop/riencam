class ViewController:
    def __init__(self, framebuffer, camera):
        self.framebuffer = framebuffer
        self.camera = camera
        self.current_view = None

    def switch_to(self, view_cls):
        if self.current_view:
            self.current_view.on_exit()

        self.current_view = view_cls(self)
        self.current_view.on_enter()
        self.current_view.render()

    def handle_input(self, event):
        if self.current_view:
            self.current_view.handle_input(event)
