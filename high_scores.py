import time
import pygame
import os
import sys

import config


class HighScores:

    default_scores = [('Nigel A.', 198300), ('A&F', 80000), ('A&F', 70000), ('A&F', 60000),
                      ('A&F', 50000), ('A&F', 40000), ('A&F', 30000), ('A&F', 20000),
                      ('A&F', 10000), ('nerdSezzer', 5000)]

    def __init__(self):
        self.scores = HighScores.default_scores
        return

    def update_high_scores(self, new_name, new_score):
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
    def process_events_for_input():
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

    def well_done_screen(self, window, font, clock, fps):
        delay = 40
        name = ""
        take_input = True
        window.fill([0, 0, 0])
        while delay:
            time.sleep(0.05)

            text_surface = font.render("Well Done", False, pygame.color.Color('yellow'))
            x = (window.get_width() - text_surface.get_width()) // 2
            window.blit(text_surface, (x, 420))

            text_surface = font.render("Please enter your name:", False, pygame.color.Color('cyan'))
            window.blit(text_surface, (300, 480))

            x = 300 + text_surface.get_width() + 20
            if take_input:
                key = self.process_events_for_input()
                if key:
                    if key == -1:
                        take_input = False
                        name = ""
                    elif key == -2:
                        take_input = False
                    elif key == -3:
                        text_surface = font.render(name, False, pygame.color.Color('black'))
                        window.blit(text_surface, (x, 480))
                        name = name[:-1]
                        text_surface = font.render(name, False, pygame.color.Color('white'))
                        window.blit(text_surface, (x, 480))
                    else:
                        text_surface = font.render(name, False, pygame.color.Color('black'))
                        window.blit(text_surface, (x, 480))
                        name += key
                        text_surface = font.render(name, False, pygame.color.Color('white'))
                        window.blit(text_surface, (x, 480))
            else:
                delay -= 1

            pygame.display.flip()
            clock.tick(fps)
        return name

    def high_scores_screen(self, ctrls, window, font, clock, fps):
        while ctrls.paused:
            time.sleep(0.05)
            window.fill([0, 0, 0])
            title_font = pygame.font.Font(os.path.join('.', config.font_name), 72)
            text_surface = title_font.render("CHUCKIE EGG", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y = 120
            window.blit(text_surface, (x, y))
            y += text_surface.get_height()

            sub_title_font = font
            text_surface = sub_title_font.render("HIGH SCORES", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y += 20
            window.blit(text_surface, (x, y))
            y += text_surface.get_height()

            y += 40
            scores = self.scores
            for name, score in scores:
                index = scores.index((name, score))
                text_surface = sub_title_font.render(f"{index+1}", False, pygame.color.Color('green'))
                window.blit(text_surface, (440, y))
                text_surface = sub_title_font.render(f"{score}", False, pygame.color.Color('green'))
                window.blit(text_surface, (620-text_surface.get_width(), y))
                text_surface = sub_title_font.render(name, False, pygame.color.Color('green'))
                window.blit(text_surface, (640, y))
                y += text_surface.get_height()
                y += 10

            start_one = font
            text_surface = start_one.render("Press S to start", False, pygame.color.Color('yellow'))
            x = (config.window_width - text_surface.get_width()) // 2
            y += 40
            window.blit(text_surface, (x, y))

            pygame.display.flip()
            clock.tick(fps)
            ctrls.process_events(None)

        return
