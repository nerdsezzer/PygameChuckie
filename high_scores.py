import pygame
import os
import sys

import config


class HighScores:
    """
    Class to manage the high scores list, just like on the Acorn, the list doesn't
    (yet?) persist outside of runtime.
    """

    default_scores = [('Nigel A.', 198300), ('A&F', 80000), ('A&F', 70000), ('A&F', 60000),
                      ('A&F', 50000), ('A&F', 40000), ('A&F', 30000), ('A&F', 20000),
                      ('A&F', 10000), ('nerdSezzer', 5000)]

    def __init__(self, _surface: pygame.Surface, _clock: pygame.time):
        self.surface = _surface
        self.clock = _clock
        self.scores = HighScores.default_scores
        self.font = pygame.font.Font(os.path.join('.', config.font_name), 36)
        return

    def update(self, new_score):
        """
        Display the 'well done' screen, and get the input for name, add
        the new name and score into the scores, and display them using
        a new Controls (to reset keypress buffers) and wait for 's' to start.
        """
        name = self.well_done_screen()
        if name:
            self.add_new_score(name, new_score)
        self.display()
        return

    def add_new_score(self, new_name, new_score):
        """
        Inserts the new name and score into the high scores list.
        """
        for name, score in self.scores:
            if new_score > score:
                x = self.scores.index((name, score))
                n = self.scores[:x]
                n.append((new_name, new_score))
                n += self.scores[x:-1]
                self.scores = n
                return
        return

    @staticmethod
    def process_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    print("done.")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -1
                if event.key == pygame.K_RETURN:
                    return -2
                if event.key == pygame.K_BACKSPACE:
                    return -3
                return event.unicode
        return

    def well_done_screen(self):
        """
        Display 'well done' and use a specific Controls capture input as name for high score.
        """
        self.surface.fill([0, 0, 0])
        name = ""

        take_input = True
        while take_input:
            text_surface = self.font.render("Well Done", False, pygame.color.Color('yellow'))
            x = (self.surface.get_width() - text_surface.get_width()) // 2
            self.surface.blit(text_surface, (x, 420))

            text_surface = self.font.render("or press Esc to skip", False, pygame.color.Color('yellow'))
            x = (self.surface.get_width() - text_surface.get_width()) // 2
            self.surface.blit(text_surface, (x, 540))

            text_surface = self.font.render("Please enter your name:", False, pygame.color.Color('cyan'))
            self.surface.blit(text_surface, (300, 480))

            x = 300 + text_surface.get_width() + 20
            if take_input:
                key = self.process_events()
                if key:
                    if key == -1:
                        take_input = False
                        name = ""
                    elif key == -2:
                        take_input = False
                    elif key == -3:
                        text_surface = self.font.render(name, False, pygame.color.Color('black'))
                        self.surface.blit(text_surface, (x, 480))
                        name = name[:-1]
                        text_surface = self.font.render(name, False, pygame.color.Color('white'))
                        self.surface.blit(text_surface, (x, 480))
                    else:
                        text_surface = self.font.render(name, False, pygame.color.Color('black'))
                        self.surface.blit(text_surface, (x, 480))
                        name += str(key)
                        text_surface = self.font.render(name, False, pygame.color.Color('white'))
                        self.surface.blit(text_surface, (x, 480))

            pygame.display.flip()
            self.clock.tick(config.fps)
        return name

    @staticmethod
    def wait_for_s_key():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    print("done.")

            if event.type == pygame.KEYDOWN:
                if event.key == ord('s'):
                    return False
        return True

    def display(self):
        """
        Display the high scores until the user presses the 's' key.
        """
        while self.wait_for_s_key():

            self.surface.fill([0, 0, 0])
            title_font = pygame.font.Font(os.path.join('.', config.font_name), 72)
            text_surface = title_font.render("CHUCKIE EGG", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y = 120
            self.surface.blit(text_surface, (x, y))
            y += text_surface.get_height()

            text_surface = self.font.render("HIGH SCORES", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y += 20
            self.surface.blit(text_surface, (x, y))
            y += text_surface.get_height()

            y += 40
            scores = self.scores
            for name, score in scores:
                index = scores.index((name, score))
                text_surface = self.font.render(f"{index+1}", False, pygame.color.Color('green'))
                self.surface.blit(text_surface, (440, y))
                text_surface = self.font.render(f"{score}", False, pygame.color.Color('green'))
                self.surface.blit(text_surface, (620-text_surface.get_width(), y))
                text_surface = self.font.render(name, False, pygame.color.Color('green'))
                self.surface.blit(text_surface, (640, y))
                y += text_surface.get_height()
                y += 10

            text_surface = self.font.render("Press S to start", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y += 40
            self.surface.blit(text_surface, (x, y))

            pygame.display.flip()
            self.clock.tick(config.fps)
        return


if __name__ == '__main__':
    surface = pygame.display.set_mode([config.window_width, config.window_height])
    clock = pygame.time.Clock()
    pygame.init()
    hs = HighScores(surface, clock)
    hs.update(19740)
