import pygame
import sys

from config import start_paused


class Controls:
    """
    Class to collate key presses and key releases.
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
                    self.paused = not self.paused
                    print(f"paused {self.paused}")
                if event.key == ord('w'):
                    self.w_down = True
                if event.key == ord('s'):
                    self.s_down = True
                if event.key == ord('a'):
                    self.a_down = True
                if event.key == ord('d'):
                    self.d_down = True
                if event.key == pygame.K_SPACE:
                    self.space_down = True

            if event.type == pygame.KEYUP:
                if event.key == ord('w'):
                    self.w_down = False
                if event.key == ord('s'):
                    self.s_down = False
                if event.key == ord('a'):
                    self.a_down = False
                if event.key == ord('d'):
                    self.d_down = False

        return
