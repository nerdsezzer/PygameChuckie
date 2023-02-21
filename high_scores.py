import time
import pygame
import os

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
