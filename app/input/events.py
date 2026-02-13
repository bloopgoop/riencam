class InputEvent:
    def __init__(self, type, action, x=None, y=None):
        self.type = type        # "BUTTON" | "TOUCH"
        self.action = action    # "PRESS" | "RELEASE" | "MOVE"
        self.x = x
        self.y = y

class LogEvent:
    def __init__(self, level, message):
        self.type = "LOG"
        self.level = level
        self.message = message

class RedirectEvent:
    def __init__(self, to):
        self.type = "REDIRECT"
        self.to=to # GALLERY, CAMERA, SETTINGS
        