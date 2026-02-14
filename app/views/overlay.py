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

class Button(OverlayElement):
    def __init__(self, x, y, icon_w, icon_h, button_w, button_h, path, callback, label, type, action):
        self.x = x
        self.y = y
        self.icon_w = icon_w
        self.icon_h = icon_h
        self.w = button_w
        self.h = button_h
        self.path = path

        self.label = label
        self.type = type
        self.action = action
        self.callback = callback


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

    def draw(self, framebuffer, debug=True):
        framebuffer.draw_image_at(self.path, self.x, self.y, self.w, self.h)
        
        if debug:
            # Draw hitbox outline (4 corners)
            from framebuffer import rgb565
            color = rgb565(0, 255, 0)  # Green
            # Top edge
            framebuffer.draw_rect(self.x, self.y, self.w, 1, color)
            # Bottom edge
            framebuffer.draw_rect(self.x, self.y + self.h, self.w, 1, color)
            # Left edge
            framebuffer.draw_rect(self.x, self.y, 1, self.h, color)
            # Right edge
            framebuffer.draw_rect(self.x + self.w, self.y, 1, self.h, color)


    def accepts_event(self, event):
        print(self.label, "called:", "type",self.type == event.type, "action", self.action == event.action )
        return self.hit_test(event.x, event.y) and self.type == event.type and self.action == event.action

    def handle_event(self):
        if self.callback:
            return self.callback()
        return {}