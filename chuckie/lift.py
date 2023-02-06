#import turtle
import pygame
import os

import config
from config import global_w, global_h
from chuckie.thing import Thing
import chuckie.utils as utils


class Lift(Thing):

    def __init__(self, level, start_tile_x, start_tile_y, direction):
        super().__init__('lift', level)

        file = "lift-left.png" if direction == "left" else "lift-right.png"
        self.image = pygame.image.load(os.path.join('.', 'images', file)).convert()
        self.image.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        print(f"putting a lift at [{start_tile_x}, {start_tile_y}]")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        self.state = False
        self.direction = direction
        self.previous_direction = "still"
        (self.hx, self.hy) = utils.tile_to_real(start_tile_x, start_tile_y)
        return

    @property
    def hy(self):
        return self._hy

    @hy.setter
    def hy(self, value):
        self._hy = value
        self.rect.y = value
        return

    def move(self):
        """
        move the lifts, upwards.  If they reach the top, they respawn at the
        bottom of the screen.
        """
        self.hy += config.lift_default_hy_velocity
        if self.hy < (6*config.tile_height):
            self.hy = (27*config.tile_height)

        if config.debug_lifts:
            self.dump_state("lift: ")
        return
