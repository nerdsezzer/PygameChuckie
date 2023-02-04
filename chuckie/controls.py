from config import start_paused


class Controls:
    """
    Class to manage the window hooks for key presses and key releases.
    """

    def __init__(self):
        self.a_down = False
        self.d_down = False
        self.w_down = False
        self.s_down = False
        self.space_down = False
        self.paused = True if start_paused else False
        return

    def register_handlers(self, window):
        window.onkeypress(self.move_left, "a")
        window.onkeyrelease(self.move_left_end, "a")
        window.onkeypress(self.move_right, "d")
        window.onkeyrelease(self.move_right_end, "d")
        window.onkeypress(self.move_up, "w")
        window.onkeyrelease(self.move_up_end, "w")
        window.onkeypress(self.move_down, "s")
        window.onkeyrelease(self.move_down_end, "s")
        window.onkeypress(self.move_jump, "space")
        window.onkeypress(self.toggle_pause, "p")
        window.listen()
        return

    def toggle_pause(self):
        self.paused = not self.paused
        print(f"paused {self.paused}")
        return

    def move_left(self):
        self.a_down = True
        return

    def move_right(self):
        self.d_down = True
        return

    def move_up(self):
        self.w_down = True
        return

    def move_down(self):
        self.s_down = True
        return

    def move_left_end(self):
        self.a_down = False
        return

    def move_right_end(self):
        self.d_down = False
        return

    def move_up_end(self):
        self.w_down = False
        return

    def move_down_end(self):
        self.s_down = False
        return

    def move_jump(self):
        self.space_down = True
        return

    def turn_stop(self):
        return

