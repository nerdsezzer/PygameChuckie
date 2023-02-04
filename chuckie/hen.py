from random import Random
import pygame
import os

import config
from chuckie.thing import Thing
from chuckie.layout_hen import draw_hen
import chuckie.utils as utils


class Hen(Thing):

    def __init__(self, name: str, level, start_tile_x, start_tile_y, direction):
        super().__init__(name, level)

        self.image = pygame.image.load(os.path.join('.', 'images', 'hen-1.png')).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        print(f"putting an hen at [{start_tile_x}, {start_tile_y}] => {id(self)}")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        self.random = Random()
        self.random.seed()
        self.state = True
        self.actions = [self.move_up, self.move_down, self.move_left, self.move_right]

        self.direction = direction
        self.previous_direction = direction
        self.animation_step = 1

        self.hx_velocity = config.hen_default_hx_velocity if direction == "right" else 0-config.hen_default_hx_velocity
        (self.hx, self.hy) = utils.tile_to_real(start_tile_x, start_tile_y)

        self.move()
        #self.draw_func = draw_hen
        #self.draw_func(self)
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

    def draw(self):
        #return self.draw_func(self)
        return

    def choose(self, options):
        decision = self.random.randint(0, sum(options)-1)
        result = [i for i, n in enumerate(options) if n == True][decision]
        return result

    def move_up(self):
        if self.check_can_move_up_down():
            self.direction = "up"
            self.hx_velocity = 0
            self.hy_velocity = config.hen_default_hy_velocity
        return

    def move_down(self):
        if self.check_can_move_up_down():
            self.direction = "down"
            self.hx_velocity = 0
            self.hy_velocity = 0 - config.hen_default_hy_velocity
        return

    def move_left(self):
        if self.check_can_move_sideways():
            self.direction = "left"
            self.hx_velocity = 0 - config.hen_default_hx_velocity
            self.hy_velocity = 0
        return

    def move_right(self):
        if self.check_can_move_sideways():
            self.direction = "right"
            self.hx_velocity = config.hen_default_hx_velocity
            self.hy_velocity = 0
        return

    def check_can_move_sideways(self) -> bool:
        """
        This function checks to see if a sideways move is possible...

        It's overriden here because we already know what moves are possible
        for Hen's, so all we need to do if check they're on the top of a block.
        """
        (tx, ty) = utils.real_to_tile(self.hx, self.hy)
        if not utils.top_of_block(tx, ty, self.hy):
            return False
        return True

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up and down is possible, i.e. a ladder.
        This function takes the current direction of travel into account.
        """
        (tx, ty) = utils.real_to_tile(self.hx, self.hy)
        if not utils.middle_of_block(tx, ty, self.hx):
            return False
        return True

    def move(self) -> None:
        """
        The walking Hens...they stick to a fairly predicable pattern
        (thanks Dan!)
        """
        previous = self.direction

        if self.direction != 'eating':
            # our current tile....
            (tx, ty) = utils.real_to_tile(self.hx, self.hy)

            # just check we're actually going over a tile boundary...
            # if not process the move, without thinking too hard!
            if not utils.top_of_block(tx, ty, self.hy) or not utils.middle_of_block(tx, ty, self.hx):
                self.hx += self.hx_velocity
                self.hy += self.hy_velocity
                self.draw()
                return

            # get all possible directions we can move in for the current tile.
            (tx, ty) = utils.real_to_tile(self.hx, self.hy)
            possible = self.get_possible_moves(tx, ty)
            if sum(possible) == 0:
                return

            can_go_up = possible[0]
            can_go_down = possible[1]
            can_go_left = possible[2]
            can_go_right = possible[3]

            if config.debug_hens:
                hen_id = str(id(self))
                self.debug(f"{hen_id}[{tx},{ty}]: "
                           f"up={can_go_up}, down={can_go_down}, left={can_go_left}, right={can_go_right}, "
                           f"dx={self.hx_velocity}, dy={self.hy_velocity}, direction={self.direction}, was={self.previous_direction}")

            options = sum(possible)
            if options == 1:
                func = self.actions[self.choose(possible)]
                func()
            elif options == 2 and self.hx_velocity > 0 and can_go_right:
                self.move_right()
            elif options == 2 and self.hx_velocity < 0 and can_go_left:
                self.move_left()
            elif options == 2 and self.hy_velocity > 0 and can_go_up:
                self.move_up()
            elif options == 2 and self.hy_velocity < 0 and can_go_down:
                self.move_down()
            elif options == 0:
                if config.debug_hens:
                    print("Hen.move(), not possible moves available.")
            else:
                # fix it for Dan...
                # if they're walking in one direction, they won't just turn round
                # at a junction.
                if can_go_left and self.hx_velocity < 0:
                    possible[3] = False
                if can_go_right and self.hx_velocity > 0:
                    possible[2] = False
                if can_go_up and self.hy_velocity > 0:
                    possible[1] = False
                if can_go_down and self.hy_velocity < 0:
                    possible[0] = False

                # another fix for Dan...
                # if they are coming off a ladder, try and go the same direction
                # as they were going before they got on the ladder.
                if sum(possible) > 1:
                    if self.hy_velocity != 0:  # we were going up or down.
                        if can_go_left and self.previous_direction == 'left':
                            possible[3] = False
                        if can_go_right and self.previous_direction == 'right':
                            possible[2] = False

                func = self.actions[self.choose(possible)]
                func()

            next_tx = tx - 1 if self.hx_velocity < 0 else tx + 1
            if self.tile_at(next_tx, ty - 1) == 'grain':
                self.previous_direction = self.direction
                self.direction = 'eating'
                self.level.consume_grain(next_tx, ty - 1, hen_mode=True)
                self.hx_velocity = 0
                self.hy_velocity = 0
                self.animation_step = 0  # reset the step counter for eating.

        if self.direction != previous:
            self.previous_direction = previous

        self.hx += self.hx_velocity
        self.hy += self.hy_velocity
        self.draw()
        return
