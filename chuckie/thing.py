import pygame.sprite

import config
from chuckie.utils import real_to_tile, tile_width, tile_height
import chuckie.utils as utils


class Thing(pygame.sprite.Sprite):

    def __init__(self, name: str, level):
        #super().__init__()
        pygame.sprite.Sprite.__init__(self)
        #self.hideturtle()
        #self.penup()
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
        return

    def get_state(self):
        (tx, ty) = real_to_tile(self._hx, self._hy)
        return f"[{self.name}] {self.direction}: x,y=({self._hx},{self._hy}), " \
               f"tile=[{tx},{ty}], calc'd=[{self._hx/tile_width},{self._hy/tile_height}], " \
               f"dx={self.hx_velocity}, dy={self.hy_velocity}, y_velocity={self.y_velocity}, " \
               f"underfoot='{self.tile_at(tx, ty-2)}')"

    def dump_state(self, prefix=""):
        print(prefix+self.get_state())
        return

    def debug(self, s: str):
        if config.debug_display:
            print(f"{self.name}: {s}")
        return

    def get_possible_moves(self, tx, ty):
        """
        Returns a list of bools, that denote if a Harry or a Hen can go
        up, down, left or right, in that order.
        """
        moves = [False, False, False, False]
        if self.tile_at(tx, ty+1) == 'ladder' and self.name == "hen":
            moves[0] = True
        if self.tile_at(tx, ty) == 'ladder' and self.name == "harry":
            moves[0] = True
        if self.tile_at(tx, ty-2) == 'ladder':
            moves[1] = True
        if self.tile_at(tx-1, ty-2) == 'floor' or self.tile_at(tx-1, ty-2) == 'ladder':
            moves[2] = True
        if self.tile_at(tx+1, ty-2) == 'floor' or self.tile_at(tx+1, ty-2) == 'ladder':
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
        return self.tile_at(tx, ty-1) == 'ladder' and utils.middle_of_block(tx, ty - 1, x)

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
        return self.get_lift() is not None

    def get_lift(self):
        """
        This checks to see if the tile at Harry's feet is a lift tile.  This
        also checks the next tile if we're not on a full tile.
        """
        tx, ty = utils.real_to_tile(self._hx + self.hx_velocity, self._hy + self.hy_velocity)
        remainder = self._hx % tile_width
        ty -= 1
        for lift in self.level.lifts:
            lift_tx, lift_ty = utils.real_to_tile(lift.hx, lift.hy)
            if tx == lift_tx and ty == lift_ty:
                return lift
            if remainder > 0:
                other_tx = int((self._hx + self.hx_velocity) / tile_width)
                if other_tx == lift_tx and ty == lift_ty:
                    return lift
        return None

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
