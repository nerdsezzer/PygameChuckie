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

        self.images_left_right = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'harry-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_left_right.append(img)

        self.images_up_down = []
        for i in range(1, 5):
            img = pygame.image.load(os.path.join('.', 'images', 'harry-ladder-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_up_down.append(img)

        self.images = self.images_left_right
        self.image = self.images[0]
        self.animation_step = -1

        print(f"putting harry at [{start_tile_x}, {start_tile_y}]")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        #self.state = False
        self.on_lift = False
        self.direction = start_direction
        self.previous_direction = "still"
        self.hx, self.hy = tile_to_real(start_tile_x, start_tile_y)
        self.draw()
        return

    def draw(self):
        """
        Figure out what sprite image is needed, Harry has two modes, up-down or
        left-right.  Both comprise a set of 4 images.
        """
        # which set of images are we using?
        if (self.direction == 'up' and self.is_going_up()) or (self.direction == 'down' and self.is_going_down()):
            self.images = self.images_up_down
        else:
            self.images = self.images_left_right

        # increment, and wrap if necessary, the animation step.
        self.animation_step += 1
        if self.animation_step == len(self.images):
            self.animation_step = 0

        # make him stand still on the lift... or jogs on the spot!
        if self.on_lift:
            self.animation_step = 2

        # now figure out which image to use.
        if self.is_going_right() or (self.on_lift and self.direction == 'right'):
            self.image = self.images[self.animation_step]
        elif self.is_going_left() or (self.on_lift and self.direction == 'left'):
            self.image = pygame.transform.flip(self.images[self.animation_step], True, False)
        elif (self.is_going_up() or self.is_going_down()) and not self.direction == 'jump':
            self.image = self.images[self.animation_step]
        else:
            if self.previous_direction == 'left':
                self.image = pygame.transform.flip(self.images[self.animation_step], True, False)
            elif self.previous_direction == 'right':
                self.image = self.images[self.animation_step]
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

        # if just doing a 'within tile move' then crack on...
        if self.hx % tile_width:
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

        # we can't move up or down on a lift...
        if self.on_lift:
            return False

        # if we're not in the middle of a block we can't go up or down, end of.
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

            # check under his feet is a ladder, and we're going up!
            if under_element == 'ladder' and self.is_going_up():
                return True

            # stop him climbing over the end of the ladder
            upper_element = self.element_at_head_level()
            if upper_element != 'ladder' and self.is_going_up():
                return False

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
            # this fixes the 'double(buffered) jump' bug... also needed in pygame version.
            ctrls.space_down = False
            return

        self.hx_velocity = 0
        self.hy_velocity = 0 if not self.on_lift else config.lift_default_hy_velocity

        if ctrls.a_down:
            self.direction = 'left'
            self.hx_velocity = 0 - config.harry_default_hx_velocity

        if ctrls.d_down:
            self.direction = 'right'
            self.hx_velocity = config.harry_default_hx_velocity

        if ctrls.w_down and not self.on_lift:
            self.direction = 'up'
            self.hy_velocity = 0 - config.harry_default_hy_velocity

        if ctrls.s_down and not self.on_lift:
            self.direction = 'down'
            self.hy_velocity = config.harry_default_hy_velocity

        if ctrls.space_down:
            ctrls.space_down = False
            self.direction = "jump"
            self.y_velocity = jump_height
            self.hy_velocity = self.y_velocity

        return

    def process_fall(self) -> None:
        """
        Updates Harry's coordinates, given that he is falling.  Check to see if
        he lands on a floor tile, updates direction and deltas if this happens.
        """
        # work out new position
        self.hy += self.hy_velocity

        # check to see if we've landed.
        under_element = self.element_under_foot(calc_next_position=False)
        if under_element == 'floor':
            print("landed.")
            self.direction = self.previous_direction
            self.y_velocity = 0
            self.hy_velocity = 0
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
        Updates Harry's coordinates, given that he is jumping.  Do the maths,
        update his current location, and check to see if either he can grab a
        ladder as he flies past, or whether he's landed.
        """
        self.y_velocity += gravity
        self.hy_velocity = self.y_velocity
        if self.on_lift:
            # we need an extra boost when jumping on or from a lift
            print("jumping from lift... double oomph")
            self.hy_velocity += 2 * config.lift_default_hy_velocity
            self.on_lift = False

        #self.dump_state("jump[b]: ")

        # limit the fall velocity, or he might 'miss' floor tiles.
        if self.hy_velocity > config.max_fall_velocity:
            self.hy_velocity = config.max_fall_velocity

        # work out new position
        x = self.hx + self.hx_velocity
        y = self.hy + self.hy_velocity
        tx, ty = real_to_tile(x, y)

        #at_foot = self.element_at_foot_level(calc_next_position=True)
        under_foot = self.element_under_foot(calc_next_position=True)

        if self.is_going_down() and under_foot == 'floor':
            # he's falling and hits floor.
            self.hy_velocity = 0
            self.y_velocity = 0
            self.direction = self.previous_direction
            self.hx += self.hx_velocity
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
            print(f"we're going up!! lift at {lift.hx},{lift.hy}")
            # lift_x, lift_y = lift.hx, lift.hy
            self.hy_velocity = 0
            self.y_velocity = 0
            self.direction = "right" if prev_delta_hx > 0 else "left"
            self.on_lift = True
            self.hy_velocity = config.lift_default_hy_velocity
            self.hx_velocity = 0
            self.hy = lift._hy - (2 * tile_height)

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
                if self.element_at_foot_level(calc_next_position=False, update_x_only=True) == 'floor':
                    # harry walked into a wall at his feet.
                    self.previous_direction = self.direction
                    self.direction = "still"
                    self.hx_velocity = 0
                else:
                    # did he walk off the edge ... of a lift?
                    if self.on_lift:
                        lift = self.get_lift()
                        if lift:
                            remainder = self.rect.centerx % tile_width
                            if (lift.direction == 'left' and remainder < (tile_width//4)) \
                                    or (lift.direction == 'right' and remainder > 3 * (tile_width//4)):
                                print("Falling off a lift.")
                                self.previous_direction = self.direction
                                self.direction = 'falling'
                                self.on_lift = False
                                self.hx_velocity = 0
                                self.hy_velocity = config.harry_falling_hy_velocity
                                return
                            else:
                                # update the hx value...
                                self.hx += self.hx_velocity

                    # ... or off the edge of a floor tile?
                    elif utils.middle_of_block(self.hx) \
                            and not (self.element_under_foot(calc_next_position=False, update_x_only=True) == 'floor'
                                or self.element_under_foot(calc_next_position=False, update_x_only=True) == 'ladder'):
                        print("Falling")
                        self.previous_direction = self.direction
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
        element = self.object_at_foot_level(calc_next_position=False)
        if element and element.name == 'egg':
            self.level.consume_egg(element)
        if element and element.name == "grain":
            self.level.consume_grain(element)

        # @todo this is not the best fix, it's to stop him walking on eggs that are next to step drops
        # be best if he didnt walk on eggs!
        #element = self.object_under_foot(calc_next_position=False)
        #if element and element.name == 'egg':
        #    self.level.consume_egg(element)
        #if element and element.name == "grain":
        #    self.level.consume_grain(element)

        return True

