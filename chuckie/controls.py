import pygame
import sys

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
        self.quit = False
        return

    def __str__(self):
        s = "["
        s += "Up" if self.w_down else "--"
        s += "|"
        s += "Dw" if self.s_down else "--"
        s += "|"
        s += "Lf" if self.a_down else "--"
        s += "|"
        s += "Rt" if self.d_down else "--"
        s += "]"
        return f"{s}, space={self.space_down}, paused={self.paused}"

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    self.quit = True

            if event.type == pygame.KEYDOWN:
                if event.key == ord('p') or event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                if event.key == ord('w'):
                    self.move_up()
                if event.key == ord('s'):
                    self.move_down()
                if event.key == ord('a'):
                    self.move_left()
                if event.key == ord('d'):
                    self.move_right()
                if event.key == pygame.K_SPACE:
                    self.move_jump()

            if event.type == pygame.KEYUP:
                if event.key == ord('w'):
                    self.move_up_end()
                if event.key == ord('s'):
                    self.move_down_end()
                if event.key == ord('a'):
                    self.move_left_end()
                if event.key == ord('d'):
                    self.move_right_end()

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
