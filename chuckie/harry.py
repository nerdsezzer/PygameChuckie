import config
import pygame
import os

from config import gravity, tile_width, tile_height, jump_height
from chuckie.thing import Thing, DIR, STATE
import chuckie.utils as utils


class Harry(Thing):
    """
    The main character: Hen House Harry...

    Harry's self.state values:  'jump', 'falling', 'walking', 'still'
    Harry's self.direction values: 'left', 'right', 'up', 'down', and 'splat'
    """

    def __init__(self, level, start_tile_x, start_tile_y, start_direction):
        super().__init__('harry', level, start_tile_x, start_tile_y, start_direction)

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

        self.image = self.images_left_right[0]
        self.init_rect(self.image, start_tile_x, start_tile_y)

        if config.debug_harry:
            print(f"putting harry at [{start_tile_x}, {start_tile_y}]")

        self.state = STATE.STILL
        self.on_lift = False

        self.dump_state()
        self.draw()
        return

    def __str__(self):
        s = super().__str__()
        return f"{s}, " \
               f"calc'd=[{(self.x / tile_width):.2f},{(self.y / tile_height):.2f}], " \
               f"y_velocity={self.y_velocity}, " \
               f"under={self.level.element_at(self.tx, self.ty+1)} "

    def draw(self):
        """
        Figure out what sprite image is needed, Harry has two modes, up-down or
        left-right.  Both comprise a set of 4 images.
        """
        # increment, and wrap if necessary, frame value.
        self.frame += 1
        if self.frame == 4:
            self.frame = 0

        self.rect.x = self.x
        self.rect.y = self.y

        # make him stand still on the lift.
        if self.on_lift:
            self.frame = 2

        def by_deltas():
            if self.is_going_right():
                self.image = self.images_left_right[self.frame]
            elif self.is_going_left():
                self.image = pygame.transform.flip(self.images_left_right[self.frame], True, False)
            return

        if self.state == STATE.STILL or self.state == STATE.JUMP or self.state == STATE.FALLING:
            by_deltas()
        else:
            if self.direction == DIR.RIGHT:
                self.image = self.images_left_right[self.frame]
            elif self.direction == DIR.LEFT:
                self.image = pygame.transform.flip(self.images_left_right[self.frame], True, False)
            elif (self.direction == DIR.UP or self.direction == DIR.DOWN) and self.dy != 0:
                self.image = self.images_up_down[self.frame]
            else:
                by_deltas()
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
        if not utils.top_of_block(self.y):
            return False

        # check we're not trying to walk into a step.
        if self.level.element_at(self.target_tx, self.ty) == 'floor':
            return False

        # check if, at the new position, there is a floor tile under feet.
        under_foot = self.element_under_foot(calc_next_position=True)
        if under_foot == 'floor':
            return True

        # if just doing a 'within tile move' then crack on...
        if self.x % tile_width:
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

        # if the new tile isn't a floor or ladder...
        # it might be a fall so return True that we can make the move, even though it's a
        # bad idea for Harry!

        # However, don't go sideways if we're on a ladder already.
        current_element = self.element_under_foot(calc_next_position=False)
        if current_element == 'ladder':
            return False

        # return True, we can move... even though we're likely to fall.
        return True

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
        if not utils.middle_of_block(self.x):
            return False

        under_element = self.element_under_foot(calc_next_position=False)

        # check there is a ladder at his feet (i.e. the bottom tile).
        lower_element = self.element_at_foot_level(calc_next_position=False)
        if lower_element == 'ladder':

            # if we're only partially through a block, return true.
            if not utils.top_of_block(self.y):
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
        if self.state == STATE.JUMP:
            # this fixes the 'double(buffered) jump' bug... also needed in pygame version.
            ctrls.space_down = False
            return

        self.dx = 0
        self.dy = 0 if not self.on_lift else config.lift_hy_velocity

        if ctrls.a_down:
            self.direction = DIR.LEFT
            self.dx = 0 - config.harry_hx_velocity

        if ctrls.d_down:
            self.direction = DIR.RIGHT
            self.dx = config.harry_hx_velocity

        if ctrls.w_down and not self.on_lift:
            self.direction = DIR.UP
            self.dy = 0 - config.harry_default_hy_velocity

        if ctrls.s_down and not self.on_lift:
            self.direction = DIR.DOWN
            self.dy = config.harry_default_hy_velocity

        if ctrls.space_down:
            ctrls.space_down = False
            self.state = STATE.JUMP
            self.y_velocity = jump_height
            self.dy = self.y_velocity

        return

    def process_fall(self) -> None:
        """
        Updates Harry's coordinates, given that he is falling.  Check to see if
        he lands on a floor tile, updates direction and deltas if this happens.
        """
        # work out new position
        self.y += self.dy

        # check to see if we've landed.
        pt = (self.rect.midbottom[0]+self.dx, self.rect.midbottom[1]+self.dy)
        obj = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        if obj and obj.name == 'floor':
            self.x = self.x + self.dx
            self.y = obj.rect.top - self.rect.height
            self.state = STATE.STILL
            self.y_velocity = 0
            self.dy = 0
        return

    def process_lift(self) -> None:
        """
        Updates Harry's coordinates, given that he's on the lift.
        It's fairly easy! ;)
        """
        # work out new position
        self.y += self.dy
        return

    def process_jump(self, w_key_down: bool, s_key_down: bool) -> None:
        """
        Updates Harry's coordinates, given that he is jumping.  Do the maths,
        update his current location, and check to see if either he can grab a
        ladder as he flies past, or whether he's landed.
        """
        self.y_velocity += gravity
        self.dy = self.y_velocity
        if self.on_lift:
            # we need an extra boost when jumping on or from a lift
            self.dy += 1.5 * config.jump_height
            self.on_lift = False

        # limit the fall velocity, or he might 'miss' floor tiles.
        if self.dy > config.max_fall_velocity:
            self.dy = config.max_fall_velocity

        # Check if harry can land on the floor.
        # When jumping, use the 'target' location and see if there is a
        # floor tile, if so snap to it.  This stops him being draw under
        # the floor level before snapping back to the top of the tile.
        pt = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + self.dy
        obj = next(iter([r for r in self.level.all_landables() if r.rect.collidepoint(pt)]), None)
        if self.is_going_down() and obj and obj.name == 'floor':
            self.x = self.x + self.dx
            self.y = obj.rect.top - self.rect.height
            self.state = STATE.STILL
            self.dy = 0
            self.y_velocity = 0
            return

        if self.is_going_down() and obj and obj.name == 'lift':
            self.x = self.x + self.dx
            self.y = obj.rect.top - self.rect.height
            self.state = STATE.STILL
            self.dy = 0
            self.y_velocity = 0
            self.on_lift = True
            self.dy = config.lift_hy_velocity
            self.dx = 0
            return

        if (w_key_down or s_key_down) \
                and utils.middle_of_block(self.x + self.dx) \
                and obj and obj.name == 'ladder':
            # he's jumping 'through' a ladder, grab it!
            # update x and y, make sure both snap to the ladder's full tile.
            self.x = obj.rect.x
            self.y = obj.rect.y - self.rect.height
            self.state = STATE.STILL
            self.dy = 0
            self.y_velocity = 0
            return

        self.x += self.dx
        self.y += self.dy
        return

    def check_lift_fall(self):
        pt = self.rect.midbottom[0], self.rect.midbottom[1] + 1
        lift = next(iter([r for r in self.level.all_landables() if r.rect.collidepoint(pt)]), None)
        if not lift or lift.name != 'lift':
            return False

        fall = False
        remainder = (self.rect.centerx + self.dx) % tile_width
        if lift.direction == DIR.LEFT and self.is_going_left():
            if remainder <= (tile_width//4):
                fall = True
        elif lift.direction == DIR.RIGHT and self.is_going_right():
            if remainder >= (3 * (tile_width//4)):
                fall = True

        if fall:
            self.x += self.dx   # let him 'take' the step... and then fall.
            self.on_lift = False
            self.state = STATE.FALLING
            self.dx = 0
            self.dy = config.harry_falling_hy_velocity
        else:
            # update the hx value...
            self.state = STATE.WALKING
            self.x += self.dx
        return True

    def check_edge_falling(self):
        fall = False
        pt = self.rect.midbottom[0]-(config.harry_hx_velocity if self.is_going_left() else 0), self.rect.midbottom[1] + 1
        element = next(iter([r for r in self.level.all_landables() if r.rect.collidepoint(pt)]), None)
        if not element or (element.name != 'floor' and element.name != 'ladder'):
            fall = True

        if fall:
            self.x += self.dx   # take the step thou...
            self.state = STATE.FALLING
            self.dx = 0
            self.dy = config.harry_falling_hy_velocity
        else:
            # update the hx value...
            self.state = STATE.WALKING
            self.x += self.dx
        return

    def process_move(self) -> None:
        """
        Based on delta values which were set up when processing key presses,
        decide if the move is valid.

        check_can_move_sideways() and check_can_move_up_down() doing alot
        of the heavy lifting here.
        """
        # if we're moving, the speed and direction will have been updated
        # by the keypress handlers above.  So we need to check if we can
        # make the move, before updating the hx and hy co-ordinates.
        if self.dx != 0:

            # check if we can make a sideways move...
            if not self.check_can_move_sideways():
                self.state = STATE.STILL
                self.dx = 0
            else:
                # did he walk off the edge ... of a lift?
                if self.on_lift:
                    self.check_lift_fall()
                else:
                    self.check_edge_falling()

        if self.dy != 0 and not self.on_lift and self.state != STATE.FALLING and self.state != STATE.JUMP:

            # check if we can move up or down...
            if self.check_can_move_up_down():
                self.state = STATE.WALKING
                self.y += self.dy
            else:
                self.state = STATE.STILL
                self.dy = 0

        return

    def move(self, ctrls, sounds_thread) -> bool:
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
        # if we're not falling update Harry's state based
        # on key-presses, this updates the deltas and direction values.
        if self.state != STATE.FALLING:
            self.update_based_on_controls(ctrls)

        if self.dx == 0 and self.dy == 0:
            sounds_thread.walking_off()
            return True

        if self.on_lift:
            self.process_lift()

        # check moves are valid, and update Harry's position.
        if self.state == STATE.FALLING:
            self.process_fall()
        elif self.state == STATE.JUMP:
            self.process_jump(ctrls.w_down, ctrls.s_down)
        else:
            self.process_move()

        # when we get here, self.hx and self.hy will have been updated.
        if config.debug_harry:
            print(self)

        self.draw()

        if self.dx != 0 or self.dy != 0:
            sounds_thread.walking_on(self)
        else:
            sounds_thread.walking_off()

        # check we didn't fall or jump out of the level!
        if utils.is_outside_playable_area(self):
            self.state = STATE.SPLAT
            sounds_thread.walking_off()
            return False

        # check for any consumables!
        element = self.object_at_foot_level(calc_next_position=False)
        if element and element.name == 'egg':
            self.level.consume_egg(element)
            sounds_thread.consume('egg')
        if element and element.name == "grain":
            self.level.consume_grain(element)
            sounds_thread.consume('grain')
        return True
