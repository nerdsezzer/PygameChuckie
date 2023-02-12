import pygame
import os

import config
from chuckie.thing import Thing
import chuckie.utils as utils


class Lift(Thing):

    LIFT_DISAPPEARS_AT = (6 * config.tile_height)
    LIFT_REAPPEARS_AT = (27 * config.tile_height)

    def __init__(self, level, start_tile_x, start_tile_y, direction):
        super().__init__('lift', level, start_tile_x, start_tile_y, direction)

        file = "lift-left.png" if direction == "left" else "lift-right.png"
        self.image = pygame.image.load(os.path.join('.', 'images', file)).convert()

        if config.debug_lifts:
            print(f"putting a lift at [{start_tile_x}, {start_tile_y}]")

        self.init_rect(self.image, start_tile_x, start_tile_y)
        return

    def __str__(self):
        name = "lft" + str(id(self))[-2:]
        rest = super().__str__()
        return "[" + name + "]" + rest[6:]

    def __repr__(self):
        tx, ty = utils.real_to_tile(self.x, self.hy)
        return f"<Lift ({self.x}, {self.hy}) [{tx},{ty}] speed = {self.dy}, {self.direction})>"

    def move(self):
        """
        move the lifts, upwards.  If they reach the top, they respawn at the
        bottom of the screen.
        """
        self.y += config.lift_default_hy_velocity
        if self.y < Lift.LIFT_DISAPPEARS_AT:
            self.y = Lift.LIFT_REAPPEARS_AT

        if config.debug_lifts:
            print(self)
        return
