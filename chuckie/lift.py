import pygame
import os

import config
from chuckie.thing import Thing
import chuckie.utils as utils


class Lift(Thing):

    LIFT_DISAPPEARS_AT = (6 * config.tile_height)
    LIFT_REAPPEARS_AT = (27 * config.tile_height)

    def __init__(self, level, start_tile_x, start_tile_y, direction):
        super().__init__('lift', level)

        file = "lift-left.png" if direction == "left" else "lift-right.png"
        self.image = pygame.image.load(os.path.join('.', 'images', file)).convert()
        if config.debug_lifts:
            print(f"putting a lift at [{start_tile_x}, {start_tile_y}]")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        self.state = False
        self.direction = direction
        self.previous_direction = "still"
        (self.hx, self.hy) = utils.tile_to_real(start_tile_x, start_tile_y)
        return

    def __str__(self):
        name = "lft" + str(id(self))[-2:]
        rest = super().__str__()
        return "[" + name + "]" + rest[6:]

    def __repr__(self):
        tx, ty = utils.real_to_tile(self.hx, self.hy)
        return f"<Lift ({self.hx}, {self.hy}) [{tx},{ty}] speed = {self.hy_velocity}, {self.direction})>"

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
        if self.hy < Lift.LIFT_DISAPPEARS_AT:
            self.hy = Lift.LIFT_REAPPEARS_AT

        if config.debug_lifts:
            print(self)
        return
