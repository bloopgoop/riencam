class ButtonGroup:
    def __init__(self, buttons):
        self.buttons = buttons

    def draw(self, framebuffer):
        for btn in self.buttons:
            btn.draw(framebuffer)

    def handle_touch(self, tx, ty):
        for btn in self.buttons:
            if btn.contains(tx, ty):
                # Radio behavior: deactivate all others
                for b in self.buttons:
                    b.active = False
                btn.active = True
                return btn
        return None