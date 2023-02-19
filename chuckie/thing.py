import pygame.sprite
from enum import Enum

import config
import chuckie.utils as utils


class STATE(Enum):
    STILL = 1
    WALKING = 2
    JUMP = 3
    FALLING = 4
    SPLAT = 5
    EATING = 6


class DIR(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Thing(pygame.sprite.Sprite):
    """
    This is the base class for a moveable 'thing'.
    Harry and the Hens both derive from this class.
    """
    def __init__(self, name: str, level, start_tile_x, start_tile_y, start_direction):
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self._hx, self._hy = utils.tile_to_real(start_tile_x, start_tile_y)
        self.hy_velocity = 0
        self.hx_velocity = 0
        self.y_velocity = 0
        self.name = name
        self.rect = None
        self.state = STATE.WALKING
        self.direction = start_direction
        self.frame = 1
        return

    def init_rect(self, image, start_tile_x, start_tile_y):
        self.rect = image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

    @property
    def x(self):
        return self._hx

    @x.setter
    def x(self, value):
        self._hx = value
        return

    @property
    def y(self):
        return self._hy

    @y.setter
    def y(self, value):
        self._hy = value
        return

    @property
    def dx(self):
        return self.hx_velocity

    @dx.setter
    def dx(self, value):
        self.hx_velocity = value

    @property
    def dy(self):
        return self.hy_velocity

    @dy.setter
    def dy(self, value):
        self.hy_velocity = value

    @property
    def tx(self):
        """ tx for the central lower tile """
        real_x = self._hx + (self.rect.width//2)
        x = real_x // config.tile_width
        return x

    @property
    def ty(self):
        """ ty for the central lower tile """
        real_y = self._hy + (self.rect.height//2)
        y = real_y // config.tile_height
        return y

    def __str__(self):
        return f"[{self.name}] " \
               f"({self.rect.centerx:.0f}, {self.rect.centery:.0f}), tile=[{self.tx},{self.ty}], " \
               f"dx={self.hx_velocity:.2f}, dy={self.hy_velocity:.2f}, " \
               f"'{self.direction}'|'{self.state}'"

    def dump_state(self, prefix=""):
        print(prefix+self.__str__())
        return

    def is_going_up(self):
        if self.hy_velocity < 0:
            return True
        return False

    def is_going_down(self):
        if self.hy_velocity > 0:
            return True
        return False

    def is_going_left(self):
        if self.hx_velocity < 0:
            return True
        return False

    def is_going_right(self):
        if self.hx_velocity > 0:
            return True
        return False

