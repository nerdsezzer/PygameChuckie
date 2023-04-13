"""
This module contains the Thing class, which is the base class for both
Harry and the Hens, it inherits the pygame.sprite.Sprite class, meaning
it represents an 'object' in the game.

THis module also defines the STATE and DIR Enum classes.
"""
from enum import Enum

import pygame.sprite

import chuckie.utils as utils
import config


class STATE(Enum):
    """
    An Enum class to specify possible values for State, used both by Harry
    and Hen: STILL, WALKING, JUMP, FALLING, SPLAT and EATING.
    """
    STILL = 1
    WALKING = 2
    JUMP = 3
    FALLING = 4
    SPLAT = 5
    EATING = 6


class DIR(Enum):
    """
    An Enum class to specify possible values for Direction, used by both
    Harry and Hens: Up, Down, Left, Right.
    The order is important as values can be used to index into arrays.
    """
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Thing(pygame.sprite.Sprite):
    """
    This is the base class for a moveable 'thing'.  Harry and the Hens both
    derive from this class.
    """
    def __init__(self, name: str, level, start_tile_x: int, start_tile_y: int,
                 start_direction: DIR):
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self.x, self.y = utils.tile_to_real(start_tile_x, start_tile_y)
        self.dx = 0
        self.dy = 0
        self.y_velocity = 0
        self.name = name
        self.rect = None
        self.state = STATE.WALKING
        self.direction = start_direction
        self.frame = 1
        return

    def init_rect(self, image: pygame.surface.Surface) -> None:
        """
        Util function to setup the Thing's rect, based on the initial sprite.
        :param image: The image that will be this Thing's sprite.
        """
        self.rect = image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    @property
    def tx(self):
        """ tx for the central lower tile """
        real_x = self.x + (self.rect.width//2)
        x = real_x // config.tile_width
        return x

    @property
    def ty(self):
        """ ty for the central lower tile """
        real_y = self.y + (self.rect.height//2)
        y = real_y // config.tile_height
        return y

    def __str__(self):
        return f"[{self.name}] " \
               f"({self.rect.centerx:.0f}, {self.rect.centery:.0f}), " \
               f"tile=[{self.tx},{self.ty}], " \
               f"dx={self.dx:.2f}, dy={self.dy:.2f}, " \
               f"'{self.direction}'|'{self.state}'"

    def dump_state(self, prefix="") -> None:
        print(prefix+self.__str__())

    def is_going_up(self) -> bool:
        if self.dy < 0:
            return True
        return False

    def is_going_down(self) -> bool:
        if self.dy > 0:
            return True
        return False

    def is_going_left(self) -> bool:
        if self.dx < 0:
            return True
        return False

    def is_going_right(self) -> bool:
        if self.dx > 0:
            return True
        return False
