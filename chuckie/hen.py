"""
This module contains the Hen class, which represents the strange
Emu-look-a-like hens that walk the platforms.
"""
import os
from random import Random
from typing import List

# pylint: disable=import-error
import pygame

import chuckie.utils as utils
import config
from chuckie.thing import Thing, STATE, DIR


class Hen(Thing):
    """
    This class represents the Hens.  Hens walk the platforms, and can go
    up and down the ladders.  They are some rules, for example the hens
    do not double back on themselves unless they have to, and after using
    a ladder they keep going the same direction.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, level, start_tile_x, start_tile_y, direction: DIR):
        super().__init__('hen', level, start_tile_x, start_tile_y, direction)

        self.images_left_right = []
        self.images_eating = []
        self.images_up_down = []
        self.image = self._load_images(os.path.join('.', 'images', 'hen-debug.png'))
        self.init_rect(self.image)

        if config.debug_hens:
            print(f"putting an hen at [{start_tile_x}, {start_tile_y}] => {id(self)}")

        self.previous = self.direction
        """ self.previous is used ensure the Hens keep moving the same
        direction after a ladder. """

        self.random = Random()
        self.random.seed()
        self.actions = [self.update_up, self.update_down, self.update_left, self.update_right]
        """ self.actions is an array of 'move' functions, up, down, left and
        right """

        if config.debug_hens:
            self.dump_state()

    def _load_images(self, file: str) -> pygame.surface.Surface:
        """
        Internal function to load the sprites from their image files.
        :param file: path to the debug image, if debug_display is True.
        :return: the first (default) image to draw on creation.
        """
        for i in range(1, 5):
            if not config.debug_display:
                file = os.path.join('.', 'images', 'hen-' + str(i) + '.png')
            img = pygame.image.load(file).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_left_right.append(img)

        self.images_eating = []
        for i in range(1, 5):
            if not config.debug_display:
                file = os.path.join('.', 'images', 'hen-eating-' + str(i) + '.png')
            img = pygame.image.load(file).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_eating.append(img)

        self.images_up_down = []
        for i in range(1, 5):
            if not config.debug_display:
                file = os.path.join('.', 'images', 'hen-ladder-' + str(i) + '.png')
            img = pygame.image.load(file).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_up_down.append(img)

        return self.images_left_right[0]

    def __str__(self):
        return "[hen" + str(id(self))[-2:] + "]" + super().__str__()[5:]

    def draw(self) -> None:
        """
        Figure out which image to display, there are four images for left-right,
        four for eating, and four more for going up and down.
        """
        self.frame += 1
        if self.frame == len(self.images_left_right):
            self.frame = 0

        # all hen images are three tiles wide, adjust x to compensate.
        self.rect.x = self.x
        self.rect.y = self.y

        if self.direction == DIR.UP or self.direction == DIR.DOWN:
            self.image = self.images_up_down[self.frame]
            return

        if self.state == STATE.EATING:
            self.image = self.images_eating[self.frame]
        else:
            self.image = self.images_left_right[self.frame]

        if self.direction == DIR.LEFT:
            self.image = pygame.transform.flip(self.image, True, False)

    def choose(self, options) -> int:
        """
        Returns the index of a randomly selected True value in the passed-in
        array.
        :param options:  The array of options to select from.
        :return: random index of a True value within the 'options' array.
        """
        decision = self.random.randint(0, sum(options)-1)
        result = [i for i, n in enumerate(options) if n is True][decision]
        return result

    def update_up(self) -> None:
        """ Simply function to set position and direction attributes """
        if self.direction != DIR.UP:
            self.previous = self.direction
        self.direction = DIR.UP
        self.dx = 0
        self.dy = 0 - config.hen_hy_velocity

    def update_down(self) -> None:
        """ Simply function to set position and direction attributes """
        if self.direction != DIR.DOWN:
            self.previous = self.direction
        self.direction = DIR.DOWN
        self.dx = 0
        self.dy = config.hen_hy_velocity

    def update_left(self) -> None:
        """ Simply function to set position and direction attributes """
        if self.direction != DIR.LEFT:
            self.previous = self.direction
        self.direction = DIR.LEFT
        self.dx = 0 - config.hen_hx_velocity
        self.dy = 0

    def update_right(self) -> None:
        """ Simply function to set position and direction attributes """
        if self.direction != DIR.RIGHT:
            self.previous = self.direction
        self.direction = DIR.RIGHT
        self.dx = config.hen_hx_velocity
        self.dy = 0

    def get_possible_moves(self) -> List[bool]:
        """
        Returns a list of bools, that denote if a Hen can go
        up, down, left or right, in that order.
        """
        moves = [False, False, False, False]

        above_pt = utils.tile_to_real(self.tx, self.ty - 2)
        above_element = next(iter([r.name for r in self.level.elements
                                   if r.rect.collidepoint(above_pt)]), None)

        under_pt = utils.tile_to_real(self.tx, self.ty + 1)
        under_element = next(iter([r.name for r in self.level.elements
                                   if r.rect.collidepoint(under_pt)]), None)

        left_pt = utils.tile_to_real(self.tx - 1, self.ty + 1)
        under_lf_element = next(iter([r.name for r in self.level.elements
                                      if r.rect.collidepoint(left_pt)]), None)

        right_pt = utils.tile_to_real(self.tx + 1, self.ty + 1)
        under_rt_element = next(iter([r.name for r in self.level.elements
                                      if r.rect.collidepoint(right_pt)]), None)

        if above_element == 'ladder':
            moves[0] = True
        if under_element == 'ladder':
            moves[1] = True
        if under_lf_element in ('floor', 'ladder'):
            moves[2] = True
        if under_rt_element in ('floor', 'ladder'):
            moves[3] = True
        return moves

    def check_for_grain(self) -> bool:
        """
        Check if the next tile is grain, if it is... eat it!
        This is a special routine as due to the animation, the hens have to
        check one tile ahead.
        """
        # pylint: disable=invalid-name
        tx = self.tx - 1 if self.is_going_left() else self.tx + 1
        next_tile = utils.tile_to_real(tx, self.ty)
        next_element = next(iter([r for r in self.level.elements
                                  if r.rect.collidepoint(next_tile)]), None)
        if next_element and next_element.name == 'grain':
            self.level.consume_grain(next_element, hen_mode=True)
            self.dx = 0
            self.dy = 0
            self.state = STATE.EATING
            self.frame = -1
            self.draw()
            return True
        return False

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def move(self) -> None:
        """
        The walking Hens...they stick to a fairly predicable pattern
        (thanks Dan!)
        """
        if self.state == STATE.EATING:
            if self.frame == 3:
                self.state = STATE.WALKING
                # pylint: disable=expression-not-assigned
                self.update_left() if self.direction == DIR.LEFT else self.update_right()
            self.draw()
            return

        # just check we're actually going over a tile boundary...
        # if not process the move, without thinking too hard!
        if not utils.top_of_block(self.y) or not utils.left_edge_of_block(self.x):
            self.x += self.dx
            self.y += self.dy
            self.draw()
            return

        # get all possible directions we can move in for the current tile.
        possible = self.get_possible_moves()
        if sum(possible) == 0:
            return

        if config.debug_hens:
            print(self)

        def can_go(direction: DIR):
            return possible[direction.value]

        options = sum(possible)
        if options == 1:
            # there's only one option, take it.
            func = self.actions[self.choose(possible)]
            func()
        if options == 2:
            # if there are only two options, keep going (dont u-turn).
            if self.dx > 0 and can_go(DIR.RIGHT):
                self.update_right()
            elif self.dx < 0 and can_go(DIR.LEFT):
                self.update_left()
            elif self.dy < 0 and can_go(DIR.UP):
                self.update_up()
            elif self.dy > 0 and can_go(DIR.DOWN):
                self.update_down()
            else:
                func = self.actions[self.choose(possible)]
                func()
        else:
            # fix it for Dan...
            # if they're walking in one direction, they won't just turn round
            # at a junction.
            if self.is_going_left():
                possible[DIR.RIGHT.value] = False
            if self.is_going_right():
                possible[DIR.LEFT.value] = False
            if self.is_going_up():
                possible[DIR.DOWN.value] = False
            if self.is_going_down():
                possible[DIR.UP.value] = False

            # another fix for Dan...
            # if they are coming off a ladder, try and go the same direction
            # as they were going before they got on the ladder.
            if sum(possible) > 1:
                if self.dy != 0:
                    if can_go(DIR.LEFT) and self.previous == DIR.LEFT:
                        possible[DIR.RIGHT.value] = False
                    if can_go(DIR.RIGHT) and self.previous == DIR.RIGHT:
                        possible[DIR.LEFT.value] = False

            func = self.actions[self.choose(possible)]
            func()

        if self.check_for_grain():
            # stand still to eat grain.
            self.draw()
            return

        self.x += self.dx
        self.y += self.dy
        self.draw()
