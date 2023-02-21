import pygame
import pygame.font
import os

import config
from chuckie.utils import tile_to_real


class Status:

    LEVEL_TIME = 900
    GAME_START_LIVES = 5
    NEW_LIFE_SCORE = 10000
    GRAIN_PAUSE_LENGTH = 10

    def __init__(self):
        """
        Time, starts at 900 every level, ticks down 10 every 5 seconds.
        Bonus, starts at 1000*level, ticks down 10 every 5 time ticks.
        """
        self.game_score = 0
        self.game_level = config.starting_level
        self.game_time = Status.LEVEL_TIME
        self.game_bonus = 1000 * (self.game_level+1)
        self.game_pause = 0
        self.game_lives = Status.GAME_START_LIVES
        self.game_lives_added = 0

        self._top_level_tile = 2
        self._bottom_level_tile = 4
        self._start_left = 1

        pygame.font.init()
        self._font = pygame.font.Font(os.path.join('.', config.font_name), 36)
        self._colour = (255, 165, 0)

        self.icons = pygame.sprite.Group()
        self.img = pygame.image.load(os.path.join('.', 'images', 'hat.png')).convert()
        self.img.convert_alpha()
        self.img.set_colorkey((0, 0, 0))
        self._update_icons()
        return

    def _update_icons(self):
        # work out the width of the work 'SCORE' in the font
        text_surface = self._font.render("SCORE  ", False, self._colour)

        for i in range(0, self.game_lives):
            icon = pygame.sprite.Sprite()
            icon.image = self.img
            icon.rect = self.img.get_rect()
            x = (self._start_left * config.tile_width) + text_surface.get_width()
            icon.rect.x = x + (i * icon.rect.width + 20)
            icon.rect.y = 3.5 * config.tile_height
            self.icons.add(icon)
        return

    def __repr__(self):
        return f"level={self.game_level}, lives left={self.game_lives}, time={self.game_time}, " \
               f"bonus={self.game_bonus}, score={self.game_score}, paused={self.game_pause}"

    def is_time_up(self):
        return self.game_time <= 0

    def reset_game(self):
        self.reset_new_level()
        self.game_score = 0
        self.game_level = config.starting_level
        self.game_pause = 0
        self.game_lives = Status.GAME_START_LIVES
        self.game_lives_added = 0
        return

    def reset_new_level(self):
        self.reset_time()
        self.game_bonus = 1000 * (self.game_level+1)
        return

    def reset_time(self):
        self.game_time = Status.LEVEL_TIME
        return

    def _check_score(self):
        if self.game_score - (self.game_lives_added * Status.NEW_LIFE_SCORE) > Status.NEW_LIFE_SCORE:
            print("new life!")
            # @ todo it should play a sound here! level up, maybe?
            self.game_lives_added += 1
            self.game_lives += 1
            self._update_icons()
        return

    def update_egg_collected(self):
        self.game_score += 100
        self._check_score()
        return

    def update_grain_collected(self):
        self.game_score += 50
        self.game_pause += Status.GRAIN_PAUSE_LENGTH
        self._check_score()
        return

    def time_tick(self, paused: bool):
        if not paused:
            self.update()
        return

    def update(self):
        if self.game_pause > 0:
            self.game_pause -= 1
        else:
            self.game_time -= 1
            if self.game_time % 5 == 0:
                self.game_bonus = (1000 * (self.game_level+1)) - ((Status.LEVEL_TIME-self.game_time) * 2)
            if self.game_bonus < 0:
                self.game_bonus = 0
        return

    def on_harry_died(self) -> int:
        """
        Remove a life, remove the 'hat' icon, and return number of lives left.
        """
        self.game_lives -= 1
        self.icons.sprites()[-1].kill()
        return self.game_lives

    def end_of_level(self, window, level, clock):
        step = (self.game_bonus // 10)
        while self.game_bonus > 0:
            if self.game_bonus < step:
                self.game_score += self.game_bonus
                self.game_bonus = 0
            else:
                self.game_bonus -= step
                self.game_score += step

            if self.game_bonus < 0:
                self.game_bonus = 0

            self._check_score()

            window.fill([0, 0, 0])
            self.draw(window)
            level.draw(window)
            pygame.display.flip()
            clock.tick(config.fps)

        for i in range(0, 21):
            window.fill([0, 0, 0])
            self.draw(window)
            pygame.display.flip()
            clock.tick(config.fps)

        return

    def draw(self, window):
        (x, y) = tile_to_real(self._start_left, self._top_level_tile)
        text_surface = self._font.render("SCORE  "+str(self.game_score).rjust(6, '0'), False, self._colour)
        window.blit(text_surface, (x + 20, y))

        (x, y) = tile_to_real(self._start_left, self._bottom_level_tile)
        text_surface = self._font.render("PLAYER  1", False, self._colour)
        window.blit(text_surface, (x + 20, y))

        (x, y) = tile_to_real(self._start_left + 6, self._bottom_level_tile)
        text_surface = self._font.render("LEVEL  " + str(self.game_level + 1).rjust(2, '0'), False, self._colour)
        window.blit(text_surface, (x, y))

        (x, y) = tile_to_real(self._start_left + 11.5, self._bottom_level_tile)
        text_surface = self._font.render("BONUS  " + str(self.game_bonus).rjust(2, '0'), False, self._colour)
        window.blit(text_surface, (x - 20, y))

        (x, y) = tile_to_real(self._start_left + 18, self._bottom_level_tile)
        text_surface = self._font.render("TIME  " + str(int(self.game_time)).rjust(2, '0'), False, self._colour)
        window.blit(text_surface, (x - 20, y))

        self.icons.draw(window)
        return
