import pygame.sprite

import config
from chuckie.utils import real_to_tile, tile_width, tile_height
import chuckie.utils as utils


class Thing(pygame.sprite.Sprite):

    def __init__(self, name: str, level):
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self.state = False
        self.direction = ""
        self.animation_step = 1
        self._hx = 0
        self._hy = 0
        self.hy_velocity = 0
        self.hx_velocity = 0
        self.y_velocity = 0
        self.name = name
        self.rect = None
        return

    @property
    def hx(self):
        return self._hx

    @hx.setter
    def hx(self, value):
        self._hx = value
        self.rect.x = value
        return

    @property
    def hy(self):
        return self._hy

    @hy.setter
    def hy(self, value):
        self._hy = value
        self.rect.y = value
        return

    def get_state(self):
        (tx, ty) = real_to_tile(self._hx, self._hy)
        lift = f"(lift)" if self.on_lift else ""
        return f"[{self.name}] {self.direction}{lift}: x,y=({self._hx:.2f},{self._hy:.2f}), " \
               f"tile=[{tx},{ty}], calc'd=[{(self._hx/tile_width):.2f},{(self._hy/tile_height):.2f}], " \
               f"dx={self.hx_velocity:.2f}, dy={self.hy_velocity:.2f}, y_velocity={self.y_velocity:.2f}, " \
               f"underfoot='{self.tile_at(tx, ty-2)}')"

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

    def element_under_foot(self, calc_next_position: bool = False, update_x_only: bool = False):
        if calc_next_position:
            pt = (self.rect.centerx + self.hx_velocity,
                  self.rect.y + self.hy_velocity + (config.tile_height * 2))
        else:
            if update_x_only:
                pt = (self.rect.centerx + self.hx_velocity,
                      self.rect.y + (config.tile_height * 2))
            else:
                pt = (self.rect.centerx,
                      self.rect.y + (config.tile_height * 2))
        element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        return element

    def object_under_foot(self, calc_next_position: bool = False):
        if calc_next_position:
            pt = (self.rect.centerx + self.hx_velocity,
                  self.rect.y + self.hy_velocity + (config.tile_height * 2))
        else:
            pt = (self.rect.centerx,
                  self.rect.y + (config.tile_height * 2))
        object = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        return object

    def element_at_foot_level(self, calc_next_position: bool = False):
        element = self.object_at_foot_level(calc_next_position)
        return element.name if element else None

    def object_at_foot_level(self, calc_next_position: bool = False):
        if calc_next_position:
            pt = (self.rect.centerx + self.hx_velocity,
                  self.rect.y + self.hy_velocity + (config.tile_height * 1))
        else:
            pt = (self.rect.centerx,
                  self.rect.y + (config.tile_height * 1))
        obj = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        return obj

    def get_possible_moves(self):
        """
        Returns a list of bools, that denote if a Harry or a Hen can go
        up, down, left or right, in that order.
        """
        moves = [False, False, False, False]

        over_head = (self._hx, self._hy - config.tile_height)
        over_head_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(over_head)]), None)

        head_tile = (self._hx, self._hy)
        head_tile_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(head_tile)]), None)

        under_foot = (self._hx, self._hy + (config.tile_height * 2))
        under_foot_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(under_foot)]), None)

        under_left = (self.rect.centerx - config.tile_width, self._hy + (config.tile_height * 2))
        under_left_element = next(iter([r.name for r in self.level.elements if r.rect.collidepoint(under_left)]), None)

        under_right = (self.rect.centerx + config.tile_width, self._hy + (config.tile_height * 2))
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

    def can_stand_on(self, tx, ty) -> bool:
        """
        Returns True if thing is standing on a floor or ladder tile.
        i.e. two tiles down from the possed in location.
        """
        if self.level.get(tx, ty-2) == 'floor' \
                or self.level.get(tx, ty-2) == 'ladder':
            return True
        return False

    def is_ladder(self) -> bool:
        """
        Returns True if thing is in the 'middle' of a ladder.  This works
        by checking the bottom/foot tile.
        """
        x = self._hx + self.hx_velocity
        y = self._hy + self.hy_velocity
        tx, ty = real_to_tile(x, y)
        return self.tile_at(tx, ty-1) == 'ladder' and utils.middle_of_block(x)

    def is_floor(self) -> bool:
        """
        This checks to see if the tile that Harry is standing on (i.e. ty-2)
        is a floor tile.  It also checks the next tile when it's not a full
        tile check.
        """
        tx, ty = utils.real_to_tile(self._hx + self.hx_velocity, self._hy + self.hy_velocity)
        remainder = self._hx % tile_width
        if remainder > 0:
            other_tx = int((self._hx + self.hx_velocity) / tile_width)
            if self.tile_at(other_tx, ty - 2) == 'floor':
                return True
        return self.tile_at(tx, ty-2) == 'floor'

    def is_lift(self) -> bool:
        """
        Returns True is Harry is on a lift, uses get_lift_coordinates().
        """
        lift = self.get_lift()
        if not lift:
            return False

        remainder = self.rect.centerx % config.tile_width
        if lift.direction == 'left':
            print("on left")
            if remainder < config.tile_width // 2:
                print("on left, but not enough (less than half)")
                return False
        else:
            print("on right")
            if remainder > config.tile_width // 2:
                print("on right, but not enough (less than half)")
                return False

        print("sticking with lift...")
        return True

    def get_lift(self):
        """
        This checks to see if the tile at Harry's feet is a lift tile.  This
        also checks the next tile if we're not on a full tile.
        """
        under_foot = (self.rect.centerx, self._hy + (2 * config.tile_height))
        element = next(iter([r for r in self.level.lifts if r.rect.collidepoint(under_foot)]), None)
        return element

    def at_feet_by_real(self):
        """
        Is called from Harry's process_move() to check if there's a step
        at Harry's feet that might stop him moving that way.
        """
        x = self._hx + self.hx_velocity
        tx, ty = real_to_tile(x, self._hy)
        remainder = x % tile_width
        if remainder > 0 and self.hx_velocity > 0:
            tx += 1
        return self.tile_at(tx, ty - 1)

    def tile_at(self, tx, ty):
        return self.level.get(tx, ty)
