class InputEvent:
    def __init__(self, type, action, x=None, y=None):
        self.type = type        # "BUTTON" | "TOUCH"
        self.action = action    # "PRESS" | "RELEASE" | "MOVE"
        self.x = x
        self.y = y
