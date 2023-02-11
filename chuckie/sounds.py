import threading
import time

import config


class Parameters(object):
    def __init__(self, value, note):
        self.lock = threading.Lock()
        self.value = value
        self.note = note
        return

    def update(self, new_value, note):
        self.lock.acquire()
        try:
            self.value = new_value
            self.note = note
        finally:
            self.lock.release()
        return


class SoundsThread(threading.Thread):

    def __init__(self, player):
        super().__init__(daemon=True)
        self.player = player
        self.player.set_instrument(35)
        self.walking = Parameters(False, 74)
        return

    def walking_on(self, harry):
        delta = 0
        if harry.state == 'falling':
            note = self.walking.note - 1
        elif harry.y_velocity == 0:
            if harry.direction == 'up' or harry.direction == 'down':
                note = 84
            else:
                note = 74
        else:   # jumping.
            delta = harry.y_velocity if harry.y_velocity > 0 else (0 - harry.y_velocity)
            note = 74 + (15 - delta)//2

        print(f"delta = {delta}, jump_height = {config.jump_height}, note = {note}")
        self.walking.update(True, note)
        return

    def consume(self, item: str):
        self.walking.update(True, 54)
        return

    def walking_off(self):
        self.walking.update(False, 74)
        return

    def run(self):
        print("thread starting")
        while True:
            if self.walking.value:
                note = self.walking.note
                self.player.note_on(note, 64)
                time.sleep(0.08)
                self.player.note_off(note, 64)
        return
