import turtle
import time

import config
from chuckie.utils import tile_to_real


class Status:

    def __init__(self):
        self.game_score = 0
        self.game_level = config.starting_level    # zero based to access array of level, +1 to display for user.
        self.game_time = 900
        self.game_bonus = 1000 * (self.game_level+1)
        self.game_bonus_tick = 0
        self.game_pause = 0
        self.game_lives = 5

        #self.header = turtle.Turtle()
        #self.header.hideturtle()
        #self.header.penup()
        #self.header.color("orange")

        self._top_level_tile = 12
        self._bottom_level_tile = 10
        self._start_left = -11
        self._font = ("Consolas", 28, "bold")
        return

    def is_time_up(self):
        return self.game_time <= 0

    def reset_new_level(self):
        self.game_time = 900
        self.game_bonus = 1000 * (self.game_level+1)
        return

    def reset_time(self):
        self.game_time = 900
        return

    def update_score_end_of_level(self, window):
        while self.game_bonus > 0:
            if self.game_bonus < 50:
                self.game_score += self.game_bonus
                self.game_bonus = 0
            else:
                self.game_bonus -= 75
                self.game_score += 75

            self._check_score()

            self.draw()
            time.sleep(0.01)
            window.update()
        return

    def _check_score(self):
        if self.game_score > 10000:
            self.game_score -= 10000
            self.game_lives += 1
        return

    def update_egg_collected(self):
        self.game_score += 100
        self._check_score()
        return

    def update_grain_collected(self):
        self.game_score += 50
        self.game_pause += 20
        self._check_score()
        return

    def update(self, harry=None, hens=None):
        if self.game_pause > 0:
            self.game_pause -= 1
        else:
            self.game_time -= 0.25
            self.game_bonus_tick += 1
            if self.game_bonus_tick == 5:
                self.game_bonus_tick = 0
                self.game_bonus -= 10

        self.draw(harry, hens)
        return

    def draw(self, harry=None, hens=None):
        return

        self.header.clear()

        if config.debug_display and harry and hens:
            (x, y) = tile_to_real(-5, self._top_level_tile-1)
            self.header.setposition(x, y)
            details = harry.get_state() + "\n"
            for h in hens:
                details += h.get_state() + "\n"
            self.header.write(details, align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left, self._top_level_tile)
        self.header.setposition(x + 20, y)
        self.header.write("SCORE  "+str(self.game_score).rjust(6, '0'), align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left + 18, self._top_level_tile)
        self.header.setposition(x - 20, y)
        self.header.write("LIVES  " + str(self.game_lives).rjust(2, ' '), align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left, self._bottom_level_tile)
        self.header.setposition(x + 20, y)
        self.header.write("PLAYER  1", align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left + 6, self._bottom_level_tile)
        self.header.setposition(x, y)
        self.header.write("LEVEL  " + str(self.game_level + 1).rjust(2, '0'), align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left + 12, self._bottom_level_tile)
        self.header.setposition(x - 20, y)
        self.header.write("BONUS  " + str(self.game_bonus).rjust(2, '0'), align="left", font=self._font)

        (x, y) = tile_to_real(self._start_left + 18, self._bottom_level_tile)
        self.header.setposition(x - 20, y)
        self.header.write("TIME  " + str(int(self.game_time)).rjust(2, '0'), align="left", font=self._font)
        return
