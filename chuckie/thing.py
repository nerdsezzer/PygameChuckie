import pygame.sprite
from enum import Enum

import config
from chuckie.utils import real_to_tile
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
    This is the base class for a moveable 'thing'.  Harry and the Hens
    both derive from this class.

    Harry's self.state values:  'jump', 'falling', 'walking', 'still'
    Harry's self.direction values: 'left', 'right', 'up', 'down', and 'splat'
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
        #self.rect.x = value
        return

    @property
    def y(self):
        return self._hy

    @y.setter
    def y(self, value):
        self._hy = value
        #self.rect.y = value
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
        #return int(self.rect.centerx / config.tile_width)
        # don't rely on rect's centerx, as it won't have been updated yet.
        real_x = self._hx + (self.rect.width//2)
        x = real_x / config.tile_width
        return x

    @property
    def ty(self):
        """ ty for the central lower tile """
        #return int(self.rect.centery / config.tile_height)
        real_y = self._hy + (self.rect.height//2)
        y = real_y / config.tile_height
        return y

    @property
    def tile(self):
        return self.tx, self.ty

    @property
    def target_tx(self):
        return (self.rect.centerx + self.dx) // config.tile_width

    @property
    def target_ty(self):
        return (self.rect.centery + self.dy) // config.tile_height

    def __str__(self):
        tx, ty = real_to_tile(self._hx, self._hy)
        return f"[{self.name}] " \
               f"x,y=({self._hx:.0f}, {self._hy:.0f})->[{tx:02d}, {ty:02d}], " \
               f"cen=({self.rect.centerx:.0f}, {self.rect.centery:.0f}), tile=[{self.tx},{self.ty}], " \
               f"dx={self.hx_velocity:.2f}, dy={self.hy_velocity:.2f}, " \
               f"'{self.direction}'|'{self.state}'"

    def get_state(self):
        return self.__str__()

    def dump_state(self, prefix=""):
        print(prefix+self.get_state())
        return

    def debug(self, s: str):
        if config.debug_display:
            print(f"{self.name}: {s}")
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

    def element_at_head_level(self):
        pt = (self.rect.centerx, self.rect.y)
        element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        return element

    def element_under_foot(self, calc_next_position: bool = False, update_x_only: bool = False):
        """
        returns the name of the element two tiles below the thing's current
        position.
        :param calc_next_position: "current tile" is the post-move position.
        :param update_x_only: figure out what tile, using x coord and delta.
        :return: name of the element or None.
        """
        """if calc_next_position:
            pt = (self.rect.centerx + self.hx_velocity,
                  self.rect.y + self.hy_velocity + (config.tile_height * 2))
        else:
            if update_x_only:
                pt = (self.rect.centerx + self.hx_velocity,
                      self.rect.y + (config.tile_height * 2))
            else:
                pt = (self.rect.centerx,
                      self.rect.y + (config.tile_height * 2))
        element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(pt)]), None)"""
        element = self.level.element_at(self.tx, self.ty + 1)
        return element

    def element_at_foot_level(self, calc_next_position: bool = False, update_x_only: bool = False):
        #element = self.object_at_foot_level(calc_next_position, update_x_only)
        element = self.level.element_at(self.tx, self.ty)
        return element # .name if element else None

    def object_at_foot_level(self, calc_next_position: bool = False, update_x_only: bool = False):
        if calc_next_position:
            pt = (self.rect.centerx + self.hx_velocity,
                  self.rect.y + self.hy_velocity + config.tile_height)
        else:
            if update_x_only:
                pt = (self.rect.centerx + self.hx_velocity,
                      self.rect.y + config.tile_height)
            else:
                pt = (self.rect.centerx,
                      self.rect.y + config.tile_height)
        obj = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        return obj

    def get_possible_moves(self):
        """
        Returns a list of bools, that denote if a Harry or a Hen can go
        up, down, left or right, in that order.
        """
        moves = [False, False, False, False]

        over_head = utils.tile_to_real(self.tx, self.ty-2)  # (self._hx, self._hy - config.tile_height)
        over_head_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(over_head)]), None)

        head_tile = utils.tile_to_real(self.tx, self.ty-1)  # (self._hx, self._hy)
        head_tile_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(head_tile)]), None)

        under_foot = utils.tile_to_real(self.tx, self.ty+1)   # (self._hx, self._hy + (config.tile_height * 2))
        under_foot_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(under_foot)]), None)

        under_left = utils.tile_to_real(self.tx-1, self.ty+1)  # (self.rect.centerx - config.tile_width, self._hy + (config.tile_height * 2))
        under_left_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(under_left)]), None)

        under_right = utils.tile_to_real(self.tx+1, self.ty+1)  # self.rect.centerx + config.tile_width, self._hy + (config.tile_height * 2))
        under_right_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(under_right)]), None)

        if over_head_element == 'ladder' and self.name == "hen":
            moves[0] = True
        if head_tile_element == 'ladder' and self.name == "harry":
            moves[0] = True
        if under_foot_element == 'ladder':
            moves[1] = True
        if under_left_element == 'floor' or under_left_element == 'ladder':
            moves[2] = True
        if under_right_element == 'floor' or under_right_element == 'ladder':
            moves[3] = True
        return moves
