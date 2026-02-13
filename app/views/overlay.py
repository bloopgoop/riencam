class OverlayElement:
    def draw(self, fb):
        raise NotImplementedError

    def hit_test(self, x, y) -> bool:
        return False

    def accepts_event(self, event) -> bool:
        return False
    
    def handle_event(self):
        return {}

class TextButton(OverlayElement):
    def __init__(self, x, y, w, h, label, type, action, callback):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.type = type
        self.action = action
        self.callback = callback

    def draw(self, fb):
        from font import draw_text
        from framebuffer import rgb565
        draw_text(fb, self.x + 4, self.y + 4, self.label, rgb565(255,255,255))

    def hit_test(self, x, y):
        print("x is true?", self.x <= x <= self.x + self.w)
        print("y is true?", self.y <= y <= self.y + self.h)

        print("event x", x, "overlay x", self.x, self.x + self.w)
        print("event y", y, "overlay y", self.y, self.y + self.h)

        if (
            self.x <= x <= self.x + self.w and
            self.y <= y <= self.y + self.h
        ):
            print(self.label, "did hit")
            return True
        
        return False
    
    def accepts_event(self, event):
        print(self.label, "called:", "type",self.type == event.type, "action", self.action == event.action )
        return self.hit_test(event.x, event.y) and self.type == event.type and self.action == event.action
    
    def handle_event(self):
        if self.callback:
            return self.callback()
        return {}

