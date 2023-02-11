from random import Random
import pygame
import os

import config
from chuckie.thing import Thing
import chuckie.utils as utils


class Hen(Thing):

    def __init__(self, name: str, level, start_tile_x, start_tile_y, direction):
        super().__init__(name, level, start_tile_x, start_tile_y, direction)

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

        self.random = Random()
        self.random.seed()
        self.actions = [self.move_up, self.move_down, self.move_left, self.move_right]

        self.hx_velocity = config.hen_default_hx_velocity if direction == "right" else 0-config.hen_default_hx_velocity

        self.move()
        return

    def __str__(self):
        name = "hen" + str(id(self))[-2:]
        return "[" + name + "]" + super().__str__()[5:]

    def draw(self):
        """
        Figure out which image to display, there are two for left, right (stretched out
        to four), three for eating (stretched to four) and three for going up or down
        (stretched out to four).  The image arrays are swapped depending on the hen's
        direction or state.
        """
        self.frame += 1
        if self.frame == 4:
            self.frame = 0

        if self.direction == 'up' or self.direction == 'down':
            self.images = self.images_up_down
            self.image = self.images[self.frame]
            return

        if self.state == 'eating':
            self.images = self.images_eating
            self.image = self.images[self.frame]
            if self.direction == 'left' and self.frame <= 3:
                self.rect.x -= (1*config.tile_width)
            if self.frame == 3:
                self.state = 'walking'
                self.hx_velocity = config.hen_default_hx_velocity if self.direction == 'right' else 0-config.hen_default_hy_velocity
            if self.direction == 'right':
                self.image = self.images[self.frame]
            elif self.direction == 'left':
                self.image = pygame.transform.flip(self.images[self.frame], True, False)
            return

        self.images = self.images_left_right
        if self.is_going_right():
            self.image = self.images[self.frame]
        elif self.is_going_left():
            self.image = pygame.transform.flip(self.images[self.frame], True, False)
        return

    def choose(self, options):
        decision = self.random.randint(0, sum(options)-1)
        result = [i for i, n in enumerate(options) if n == True][decision]
        return result

    def move_up(self):
        if self.check_can_move_up_down():
            self.direction = "up"
            self.hx_velocity = 0
            self.hy_velocity = 0 - config.hen_default_hy_velocity
        return

    def move_down(self):
        if self.check_can_move_up_down():
            self.direction = "down"
            self.hx_velocity = 0
            self.hy_velocity = config.hen_default_hy_velocity
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
        if not utils.top_of_block(self.hy):
            return False
        return True

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up and down is possible, i.e. a ladder.
        This function takes the current direction of travel into account.
        """
        (tx, ty) = utils.real_to_tile(self.hx, self.hy)
        if not utils.middle_of_block(self.hx):
            return False
        return True

    def move(self) -> None:
        """
        The walking Hens...they stick to a fairly predicable pattern
        (thanks Dan!)
        """
        if self.state != 'eating':
            # our current tile....
            (tx, ty) = utils.real_to_tile(self.hx, self.hy)

            # just check we're actually going over a tile boundary...
            # if not process the move, without thinking too hard!
            if not utils.top_of_block(self.hy) or not utils.middle_of_block(self.hx):
                self.hx += self.hx_velocity
                self.hy += self.hy_velocity
                self.draw()
                return

            # get all possible directions we can move in for the current tile.
            (tx, ty) = utils.real_to_tile(self.hx, self.hy)
            possible = self.get_possible_moves()
            if sum(possible) == 0:
                return

            can_go_up = possible[0]
            can_go_down = possible[1]
            can_go_left = possible[2]
            can_go_right = possible[3]

            if config.debug_hens:
                print(self)

            options = sum(possible)
            if options == 1:
                func = self.actions[self.choose(possible)]
                func()
            elif options == 2 and self.hx_velocity > 0 and can_go_right:
                self.move_right()
            elif options == 2 and self.hx_velocity < 0 and can_go_left:
                self.move_left()
            elif options == 2 and self.hy_velocity < 0 and can_go_up:
                self.move_up()
            elif options == 2 and self.hy_velocity > 0 and can_go_down:
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
                        if can_go_left and self.direction == 'left':
                            possible[3] = False
                        if can_go_right and self.direction == 'right':
                            possible[2] = False

                func = self.actions[self.choose(possible)]
                func()

            if self.is_going_left():
                next_tile = (self.hx + self.hx_velocity, self.hy + self.hy_velocity + config.tile_height)
            else:
                next_tile = (self.hx + (1*config.tile_width), self.hy + self.hy_velocity + config.tile_height)
            next_element = next(iter([r for r in self.level.elements if r.rect.collidepoint(next_tile)]), None)
            if next_element and next_element.name == 'grain':
                self.state = 'eating'
                print(f"about to be 'eating' setting state to {self.state}")
                self.level.consume_grain(next_element, hen_mode=True)
                self.hx_velocity = 0
                self.hy_velocity = 0
                self.frame = -1  # reset the step counter for eating.
                self.draw()
                return

        self.hx += self.hx_velocity
        self.hy += self.hy_velocity
        self.draw()
        return
