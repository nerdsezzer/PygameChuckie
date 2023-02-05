import config
import pygame
import os

from config import gravity, tile_width, tile_height, jump_height
from chuckie.thing import Thing
from chuckie.utils import tile_to_real, real_to_tile
import chuckie.utils as utils


class Harry(Thing):
    """
    The main character: Hen House Harry...
    """

    def __init__(self, level, start_tile_x, start_tile_y, start_direction):
        super().__init__('harry', level)

        self.images = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'harry-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images.append(img)
        self.image = self.images[0]
        self.animation_step = -1

        print(f"putting harry at [{start_tile_x}, {start_tile_y}]")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        self.state = False
        self.on_lift = False
        self.direction = start_direction
        self.previous_direction = "still"
        self.hx, self.hy = tile_to_real(start_tile_x, start_tile_y)
        self.draw()
        return

    def draw(self):
        self.animation_step += 1
        if self.animation_step >= len(self.images):
            self.animation_step = 0
        if self.hx_velocity > 0 or self.previous_direction == 'right':
            self.image = self.images[self.animation_step]
        elif self.hx_velocity < 0 or self.previous_direction == 'left':
            self.image = pygame.transform.flip(self.images[self.animation_step], True, False)
        return

    def check_can_move_sideways(self) -> bool:
        """
        This function checks to see if a move is possible, i.e. floor or ladder
        is there to step on.

        This function uses current direction of travel to determine if a
        sideways move is possible.
        """

        # just check if we're on the lift, if so... the rules are different
        if self.on_lift:
            return True

        # work out the tile we're currently on...
        if not utils.top_of_block(self.hy):
            return False

        # check if, at the new position, there is a floor tile under feet.
        under_foot = self.element_under_foot(calc_next_position=True)
        if under_foot == 'floor':
            return True

        # if we're moving left, the real co-ordinates will be reporting as
        # the next block, if this is only a 'in tile' move, just let it happen.
        if self.is_going_right() and self.hx % tile_width:
            return True

        # if the new block is a ladder then... ok
        if under_foot == 'ladder':

            # this is for when we're on the ladder or trying to get off the
            # ladder... make sure we can only move sideways on the ladder
            # if there's a valid 'floor' in the next tile.
            moves = self.get_possible_moves()
            if self.is_going_left() and not moves[2]:
                return False

            if self.is_going_right() and not moves[3]:
                return False

            return True

        # if the new tile isn't a floor or ladder, it might be a fall.
        # so return True that we can make the move, even though it's a
        # bad idea for Harry!
        if not under_foot == "ladder" and not under_foot == "floor":

            # However, don't go sideways if we're on a ladder already.
            current_element = self.element_under_foot(calc_next_position=False)
            if current_element == 'ladder':
                return False

            # return True, we can move... even though we're likely to fall.
            return True

        return False

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up or down is possible, i.e. a ladder.
        This function takes the current direction of travel into account.

        This function is overriden by Hen's as they don't need so much checking,
        as they have a get_possible_hen_moves() function.
        """

        # if we're not in the middle of a block we can't go up or down, end of.
        tx, ty = real_to_tile(self.hx, self.hy)
        if not utils.middle_of_block(self.hx):
            return False

        under_element = self.element_under_foot(calc_next_position=False)

        # check there is a ladder at his feet (i.e. the bottom tile).
        lower_element = self.element_at_foot_level(calc_next_position=False)
        if lower_element == 'ladder':

            # if we're only partially through a block, return true.
            if not utils.top_of_block(self.hy):
                return True

            # check under his feet that it's a floor, and we're going up!
            if under_element == 'floor' and self.is_going_up():
                return True

            # stop him climbing over the end of the ladder
            if self.tile_at(tx, ty) != 'ladder' and self.is_going_up():
                return False

            # check under his feet is a ladder, and we're going up!
            if under_element == 'ladder' and self.is_going_up():
                return True

            # check under his feet is a ladder, we can go down...
            if under_element == 'ladder' and self.is_going_down():
                return True

        # if there isn't a ladder in the bottom tile, is there one
        # underneath (i.e. is he at the top of the ladder).
        elif under_element == 'ladder' and self.is_going_down():
            return True

        return False

    def update_based_on_controls(self, ctrls) -> None:
        """
        Figure out what the hx_velocity and hy_velocity should be given what
        keys are pressed.
        """
        if self.direction == 'jump':
            # this stops the 'double jump' bug...
            ctrls.space_down = False
            return

        self.hx_velocity = 0
        self.hy_velocity = 0 if not self.on_lift else config.lift_default_hy_velocity

        if ctrls.a_down:
            self.state = True
            self.direction = 'left'
            self.hx_velocity = 0 - config.harry_default_hx_velocity

        if ctrls.d_down:
            self.state = True
            self.direction = 'right'
            self.hx_velocity = config.harry_default_hx_velocity

        if ctrls.w_down:
            self.state = True
            self.direction = 'up'
            self.hy_velocity = 0 - config.harry_default_hy_velocity

        if ctrls.s_down:
            self.state = True
            self.direction = 'down'
            self.hy_velocity = config.harry_default_hy_velocity

        if ctrls.space_down:
            ctrls.space_down = False
            self.direction = "jump"
            self.state = True
            self.y_velocity = jump_height
            self.hy_velocity = self.y_velocity

        return

    def process_fall(self) -> None:
        """
        Updates Harry's coordinates, given that his state is falling.
        Check to see if he lands on a floor tile, updates state if this
        happens.
        """
        # work out new position
        self.hy += self.hy_velocity

        # check to see if we've landed.
        #tx, ty = real_to_tile(self.hx, self.hy)
        #if utils.top_of_block(self.hy) and (self.tile_at(tx, ty-2) == 'floor' or self.tile_at(tx, ty-2) == 'ladder'):
        under_element = self.element_under_foot(calc_next_position=False)
        if under_element == 'floor':
            print("landed.")
            self.direction = "still"
            self.y_velocity = 0
            self.hy_velocity = 0
            self.state = False
        return

    def process_lift(self) -> None:
        """
        Updates Harry's coordinates, given that he's on the lift.
        It's fairly easy! ;)
        """
        # work out new position
        self.hy += self.hy_velocity
        return

    def process_jump(self, w_key_down: bool, s_key_down: bool, prev_delta_hx: int) -> None:
        """
        Updates Harry's coordinates, given that he is jumping.
        Do the maths, update his current location, and check to see
        if either he can grab a ladder as he flies past, or whether
        he's landed.
        """
        self.y_velocity += gravity
        self.hy_velocity = self.y_velocity
        if self.on_lift:
            # we need an extra boost when jumping on or from a lift
            self.hy_velocity += (2*config.lift_default_hy_velocity)
            self.on_lift = False

        #self.dump_state("jump[b]: ")

        # limit the fall velocity, or it'll make Harry miss floors.
        if self.hy_velocity > config.max_fall_velocity:
            self.hy_velocity = config.max_fall_velocity

        # work out new position
        x = self.hx + self.hx_velocity
        y = self.hy + self.hy_velocity
        tx, ty = real_to_tile(x, y)

        under_foot = self.element_under_foot(calc_next_position=True)
        if self.is_going_down() and (under_foot == 'floor' or under_foot == 'ladder'):
            # he's falling and hits floor.
            self.hy_velocity = 0
            self.y_velocity = 0
            self.direction = self.previous_direction
            self.hx = x
            # set y to the top of the floor tile we just landed on.
            self.hy = (y // tile_height) * tile_height

        elif (w_key_down or s_key_down) and self.is_ladder():
            # he's jumping 'through' a ladder, grab it!
            self.hy_velocity = 0
            self.y_velocity = 0
            self.direction = self.previous_direction
            # snap Harry to the full tile.
            self.hx, self.hy = tile_to_real(tx, ty)

        elif self.is_lift():
            # he's landed on a 'lift'
            lift = self.get_lift()
            lift_x, lift_y = lift.hx, lift.hy
            self.hy_velocity = 0
            self.y_velocity = 0
            self.direction = "right" if prev_delta_hx > 0 else "left"
            self.on_lift = True
            self.hy_velocity = config.lift_default_hy_velocity
            self.hx_velocity = 0
            self.hy = lift_y + (2 * tile_height)

        else:
            self.hx = x
            self.hy = y

        #self.dump_state("jump[a]: ")
        return

    def process_move(self) -> None:
        """
        Based on delta values which were setup when processing key presses,
        decide if the move is valid.

        check_can_move_sideways() and check_can_move_up_down() doing alot
        of the heavy lifting here.
        """
        # self.dump_state("before: ")

        # if we're moving, the speed and direction will have been updated
        # by the keypress handlers above.  So we need to check if we can
        # make the move, before updating the hx and hy co-ordinates.
        if self.hx_velocity != 0:

            # check if we can make a sideways move...
            if not self.check_can_move_sideways():
                self.hx_velocity = 0
            else:
                if self.element_at_foot_level(True) == 'floor':
                    # harry walked into a wall at his feet.
                    self.direction = "still"
                    self.hx_velocity = 0
                else:
                    # ... did he walk off an edge?
                    if utils.middle_of_block(self.hx) and not self.element_under_foot(calc_next_position=False, update_x_only=True):
                        print("Falling")
                        self.direction = 'falling'
                        self.on_lift = False
                        self.hx_velocity = 0
                        self.hy_velocity = config.harry_falling_hy_velocity
                        return
                    else:
                        # update the hx value...
                        self.hx += self.hx_velocity

        if self.hy_velocity != 0 and not self.on_lift:

            # check if we can move up or down...
            if self.check_can_move_up_down():
                self.hy += self.hy_velocity
            else:
                self.hy_velocity = 0

        # self.dump_state("after:  ")
        return

    def move(self, ctrls) -> bool:
        """
        Harry has an x,y position and dx,dy speeds.
        1. determine change in speed/direction from key-presses.
        2. determine if harry can make the move he's setup for.
        3. update co-ords
        4. draw Harry.
        5. check he didn't go splat ... end of screen, down hole?
        6. check for any consumables at new position.

        Return:
        True for all's ok, or
        False for not ok (i.e. we've splatted).
        """
        saved_delta_hx = self.hx_velocity

        # if we're not falling or jumping, update Harry's state based
        # on key-presses, this updates the deltas and direction values.
        if self.direction != "falling":
            self.update_based_on_controls(ctrls)

        if self.state is False:
            return True

        if self.hx_velocity == 0 and self.hy_velocity == 0:
            return True

        if self.on_lift:
            self.process_lift()

        # check moves are valid, and update Harry's position.
        if self.direction == 'falling':
            self.process_fall()
        elif self.direction == 'jump':
            self.process_jump(ctrls.w_down, ctrls.s_down, saved_delta_hx)
        else:
            self.process_move()

        # when we get here, self.hx and self.hy will have been updated.
        if config.debug_harry:
            self.dump_state("after:  ")

        self.draw()

        # check we didn't fall or jump out of the level!
        if utils.is_outside_playable_area(self):
            self.direction = "splat"
            return False

        # check for any consumables!
        tx, ty = real_to_tile(self.hx, self.hy)

        # check the tile we're most on...
        remainder = self.hx % tile_width
        if remainder > 0:
            tx = round(self.hx / tile_width)

        # ... to see if there's anything to collect/pickup.
        element = self.object_at_foot_level(calc_next_position=False)
        if element and element.name == 'egg':
            self.level.consume_egg(element)
        if element and element.name == "grain":
            self.level.consume_grain(element)

        return True

