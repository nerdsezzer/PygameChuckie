"""
This module represents the user's key presses within the game.
"""
import sys

# pylint: disable=import-error
import pygame

import config


class Controls:
    """
    Class to collate key presses and key releases.
    """

    HALF_SECOND_TICK = pygame.USEREVENT+1

    def __init__(self):
        self.a_down = False
        self.d_down = False
        self.w_down = False
        self.s_down = False
        self.space_down = False
        self.paused = config.start_paused
        self.quit = False

    def __str__(self):
        status = "["
        status += "Up" if self.w_down else "--"
        status += "|"
        status += "Dw" if self.s_down else "--"
        status += "|"
        status += "Lf" if self.a_down else "--"
        status += "|"
        status += "Rt" if self.d_down else "--"
        status += "]"
        return f"{status}, space={self.space_down}, paused={self.paused}"

    # pylint: disable=too-many-branches
    def process_events(self, tick_handler) -> None:
        """
        Function used to capture the state of the keypresses, for when needed
        by Harry, HighScores, or main game loop.
        This method captures the 500ms tick, that is used to manage the game
        time counter.
        :param tick_handler: handler for the status.update() routine.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    self.quit = True

            if event.type == Controls.HALF_SECOND_TICK and tick_handler:
                tick_handler(self.paused)

            if event.type == pygame.KEYDOWN:
                if event.key == ord('p') or event.key == pygame.K_ESCAPE \
                        or (event.key == ord('s') and not tick_handler):
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
