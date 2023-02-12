import threading
import time
import pygame


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

    def __init__(self):
        super().__init__(daemon=True)
        pygame.midi.init()
        # print(f"number of midi devices = {pygame.midi.get_count()}")
        device = pygame.midi.get_default_output_id()
        if device != -1:
            # print(f"default midi device = {device}")
            self.player = pygame.midi.Output(device)
            self.player.set_instrument(35)
        else:
            self.player = None

        self.params = Parameters(False, 74)
        return

    def walking_on(self, harry):
        if self.player:
            delta = 0
            if harry.state == 'falling':
                note = self.params.note - 1
            elif harry.y_velocity == 0:
                if harry.direction == 'up' or harry.direction == 'down':
                    note = 84
                else:
                    note = 74
            else:   # jumping.
                delta = harry.y_velocity if harry.y_velocity > 0 else (0 - harry.y_velocity)
                note = 74 + (15 - delta)//2

            # print(f"delta = {delta}, jump_height = {config.jump_height}, note = {note}")
            self.params.update(True, note)
        return

    def consume(self, item: str):
        if self.player:
            self.params.update(True, 54)
        return

    def walking_off(self):
        if self.player:
            self.params.update(False, 74)
        return

    def run(self):
        if self.player:
            while True:
                if self.params.value:
                    note = self.params.note
                    self.player.note_on(note, 64)
                    time.sleep(0.08)
                    self.player.note_off(note, 64)
        return
