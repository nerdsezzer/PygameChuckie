from random import Random
import pygame
import os

import config
from chuckie.thing import Thing, STATE, DIR
import chuckie.utils as utils


class Hen(Thing):

    def __init__(self, level, start_tile_x, start_tile_y, direction: DIR):
        super().__init__('hen', level, start_tile_x, start_tile_y, direction)

        self.images_left_right = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'hen-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_left_right.append(img)

        self.images_eating = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'hen-eating-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_eating.append(img)

        self.images_up_down = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'hen-ladder-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_up_down.append(img)

        self.images = self.images_left_right
        self.image = self.images[0]
        self.init_rect(self.image, start_tile_x, start_tile_y)

        if config.debug_hens:
            print(f"putting an hen at [{start_tile_x}, {start_tile_y}] => {id(self)}")

        self.move_left() if direction == DIR.LEFT else self.move_right()

        self.random = Random()
        self.random.seed()
        self.actions = [self.move_up, self.move_down, self.move_left, self.move_right]

        self.move()
        return

    def __str__(self):
        hen_id = "hen" + str(id(self))[-2:]
        return "[" + hen_id + "]" + super().__str__()[5:]

    def draw(self):
        """
        Figure out which image to display, there are two for left, right (stretched out
        to four), three for eating (stretched to four) and three for going up or down
        (stretched out to four).  The image arrays are swapped depending on the hen's
        direction or state.
        """
        self.frame += 1
        if self.frame == 4:     # all the image arrays are 4 in length.
            self.frame = 0

        # all images are three tiles wide, adjust display x to compensate.
        self.rect.x = self.x # - config.tile_width
        self.rect.y = self.y

        if self.direction == DIR.UP or self.direction == DIR.DOWN:
            self.images = self.images_up_down
            self.image = self.images[self.frame]
            return

        if self.state == STATE.EATING:
            self.images = self.images_eating
        else:
            self.images = self.images_left_right

        if self.direction == DIR.RIGHT:
            self.image = self.images[self.frame]
        elif self.direction == DIR.LEFT:
            self.image = pygame.transform.flip(self.images[self.frame], True, False)
        else:
            if config.debug_hens:
                print("Hen.draw(), dont know what direction to go!")
        return

    def choose(self, options):
        decision = self.random.randint(0, sum(options)-1)
        result = [i for i, n in enumerate(options) if n is True][decision]
        return result

    def move_up(self):
        self.direction = DIR.UP
        self.dx = 0
        self.dy = 0 - config.hen_hy_velocity
        return

    def move_down(self):
        self.direction = DIR.DOWN
        self.dx = 0
        self.dy = config.hen_hy_velocity
        return

    def move_left(self):
        self.direction = DIR.LEFT
        self.dx = 0 - config.hen_hx_velocity
        self.dy = 0
        return

    def move_right(self):
        self.direction = DIR.RIGHT
        self.dx = config.hen_hx_velocity
        self.dy = 0
        return

    def check_can_move_sideways(self) -> bool:
        """
        This function checks to see if a sideways move is possible...

        It's overriden here because we already know what moves are possible
        for Hen's, so all we need to do if check they're on the top of a block.
        """
        if not utils.top_of_block(self.y):
            return False
        return True

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up and down is possible, i.e. a ladder.
        """
        if not utils.middle_of_block(self.x):
            return False
        return True

    def check_for_grain(self):
        """
        Check the next tile to see if it's grain, if it is... eat it!
        """
        tx = self.tx - 1 if self.is_going_left() else self.tx + 1
        next_tile = utils.tile_to_real(tx, self.ty)
        next_element = next(iter([r for r in self.level.elements if r.rect.collidepoint(next_tile)]), None)
        if next_element and next_element.name == 'grain':
            self.level.consume_grain(next_element, hen_mode=True)
            self.dx = 0
            self.dy = 0
            self.state = STATE.EATING
            self.frame = -1
            self.draw()
            return True
        return False

    def move(self) -> None:
        """
        The walking Hens...they stick to a fairly predicable pattern
        (thanks Dan!)
        """
        if self.state == STATE.EATING:
            if self.frame == 3:
                self.state = STATE.WALKING
                self.move_left() if self.direction == DIR.LEFT else self.move_right()
            self.draw()
            return

        # just check we're actually going over a tile boundary...
        # if not process the move, without thinking too hard!
        if not utils.top_of_block(self.y) or not utils.middle_of_block(self.x):
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

        def can_go(d: DIR):
            return possible[d.value]

        options = sum(possible)
        if options == 1:
            func = self.actions[self.choose(possible)]
            func()
        elif options == 2 and self.dx > 0 and can_go(DIR.RIGHT):
            self.move_right()
        elif options == 2 and self.dx < 0 and can_go(DIR.LEFT):
            self.move_left()
        elif options == 2 and self.dy < 0 and can_go(DIR.UP):
            self.move_up()
        elif options == 2 and self.dy > 0 and can_go(DIR.DOWN):
            self.move_down()
        elif options == 0:
            if config.debug_hens:
                print("Hen.move(), not possible moves available.")
        else:
            # fix it for Dan...
            # if they're walking in one direction, they won't just turn round
            # at a junction.
            if can_go(DIR.LEFT) and self.dx < 0:
                possible[DIR.RIGHT.value] = False
            if can_go(DIR.RIGHT) and self.dx > 0:
                possible[DIR.LEFT.value] = False
            if can_go(DIR.UP) and self.dy > 0:
                possible[DIR.DOWN.value] = False
            if can_go(DIR.DOWN) and self.dy < 0:
                possible[DIR.UP.value] = False

            # another fix for Dan...
            # if they are coming off a ladder, try and go the same direction
            # as they were going before they got on the ladder.
            if sum(possible) > 1:
                if self.dy != 0:  # we were going up or down.
                    if can_go(DIR.LEFT) and self.direction == DIR.LEFT:
                        possible[DIR.RIGHT.value] = False
                    if can_go(DIR.RIGHT) and self.direction == DIR.RIGHT:
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
        return
