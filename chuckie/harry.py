import config
import pygame
import os

from config import gravity, tile_width, tile_height, jump_height
from chuckie.thing import Thing, DIR, STATE
import chuckie.utils as utils


class Harry(Thing):
    """
    The main character: Hen House Harry...
    """

    def __init__(self, level, start_tile_x, start_tile_y, start_direction):
        super().__init__('harry', level, start_tile_x, start_tile_y, start_direction)

        self.images_left_right = []
        for i in range(1, 5):
            if config.debug_display:
                img = pygame.image.load(os.path.join('.', 'images', 'harry-debug.png')).convert()
            else:
                img = pygame.image.load(os.path.join('.', 'images', 'harry-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_left_right.append(img)

        self.images_up_down = []
        for i in range(1, 5):
            if config.debug_display:
                img = pygame.image.load(os.path.join('.', 'images', 'harry-debug.png')).convert()
            else:
                img = pygame.image.load(os.path.join('.', 'images', 'harry-ladder-' + str(i) + '.png')).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_up_down.append(img)

        self.image = self.images_left_right[0]
        self.init_rect(self.image, start_tile_x, start_tile_y)

        self.step = pygame.mixer.Sound(os.path.join('.', 'step.wav'))
        self.jump = pygame.mixer.Sound(os.path.join('.', 'jump.wav'))
        self.fall = pygame.mixer.Sound(os.path.join('.', 'fall.wav'))
        self.egg = pygame.mixer.Sound(os.path.join('.', 'egg.wav'))
        self.grain = pygame.mixer.Sound(os.path.join('.', 'grain.wav'))
        self.ladder = pygame.mixer.Sound(os.path.join('.', 'ladder.wav'))

        if config.debug_harry:
            print(f"putting harry at [{start_tile_x}, {start_tile_y}]")

        self.state = STATE.STILL
        self.on_lift = False

        self.draw()
        return

    def __str__(self):
        return f"{super().__str__()}, y_velocity={self.y_velocity}, " \
               f"under={self.level.element_at(self.tx, self.ty+1)} "

    def draw(self):
        """
        Figure out which sprite image is needed, Harry has two modes, up-down or
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
                self.step.play()
                self.image = self.images_left_right[self.frame]
            elif self.direction == DIR.LEFT:
                self.step.play()
                self.image = pygame.transform.flip(self.images_left_right[self.frame], True, False)
            elif (self.direction == DIR.UP or self.direction == DIR.DOWN) and self.dy != 0:
                self.ladder.play()
                self.image = self.images_up_down[self.frame]
            else:
                by_deltas()
        return

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
            self.jump.play()
            ctrls.space_down = False
            self.state = STATE.JUMP
            self.y_velocity = jump_height
            self.dy = self.y_velocity

        return

    def get_possible_moves(self):
        """
        Returns a list of bools, that denote if Harry can go
        up, down, left or right, in that order.
        Harry can go left and right as long as there isn't a
        floor tile 'step'.
        """
        moves = [False, False, True, True]

        items = self.level.all_landables()
        head_tile = utils.tile_to_real(self.tx, self.ty-1)
        head_tile_element = next(iter([r.name for r in items if r.rect.collidepoint(head_tile)]), "")

        current_tile = utils.tile_to_real(self.tx, self.ty)
        current_element = next(iter([r.name for r in items if r.rect.collidepoint(current_tile)]), "")

        under_foot = utils.tile_to_real(self.tx, self.ty+1)
        under_foot_element = next(iter([r.name for r in items if r.rect.collidepoint(under_foot)]), "")

        left = utils.tile_to_real(self.tx-1, self.ty)
        left_element = next(iter([r.name for r in items if r.rect.collidepoint(left)]), "")

        under_left = utils.tile_to_real(self.tx-1, self.ty+1)
        under_left_element = next(iter([r.name for r in items if r.rect.collidepoint(under_left)]), "")

        right = utils.tile_to_real(self.tx+1, self.ty)
        right_element = next(iter([r.name for r in items if r.rect.collidepoint(right)]), "")

        under_right = utils.tile_to_real(self.tx+1, self.ty+1)
        under_right_element = next(iter([r.name for r in items if r.rect.collidepoint(under_right)]), "")

        if head_tile_element == 'ladder' or current_element == 'ladder':
            moves[0] = True
        if under_foot_element == 'ladder':
            moves[1] = True
        if left_element == 'floor':
            moves[2] = False
        if right_element == 'floor':
            moves[3] = False

        if current_element == 'ladder':
            if under_left_element == "" or under_left_element == 'grain' or under_left_element == 'egg':
                moves[2] = False
            if under_right_element == "" or under_right_element == 'grain' or under_right_element == 'egg':
                moves[3] = False

        return moves

    def check_can_move_sideways(self) -> bool:
        """
        This function checks to see if a move is possible, i.e. there's a
        floor or ladder to step on.
        """
        # if just doing a 'within tile move' then crack on...
        if self.x % tile_width:
            return True

        # if we're not on the top of a block, we can't go sideways.
        if utils.top_of_block(self.y):
            moves = self.get_possible_moves()
            if self.is_going_left() and moves[DIR.LEFT.value]:
                return True
            if self.is_going_right() and moves[DIR.RIGHT.value]:
                return True
        return False

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up or down is possible, i.e. we're on a ladder.
        """
        if utils.left_edge_of_block(self.x):
            moves = self.get_possible_moves()
            if self.is_going_up() and moves[DIR.UP.value]:
                return True
            if self.is_going_down() and moves[DIR.DOWN.value]:
                return True
        return False

    def process_fall(self) -> None:
        """
        Updates Harry's coordinates, given that he is falling.  Check to see if
        he lands on a floor tile, updates direction and deltas if this happens.
        """
        # work out new position.
        self.y += self.dy

        # check to see if we've landed.
        pt = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + self.dy
        obj = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        if obj and obj.name == 'floor':
            self.x = self.x + self.dx
            self.y = obj.rect.top - self.rect.height
            self.state = STATE.STILL
            self.y_velocity = 0
            self.dy = 0
        return

    def process_jump(self, w_key_down: bool, s_key_down: bool) -> None:
        """
        Updates Harry's coordinates, given that he is jumping.  Do the maths,
        update his current location, and check to see if either he can grab a
        ladder as he flies past, or whether he's landed on a floor, or lift.
        """
        self.y_velocity += gravity
        self.dy = self.y_velocity

        # we need an extra boost when jumping on or from a lift
        if self.on_lift:
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
                and utils.left_edge_of_block(self.x + self.dx) \
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

    def process_lift(self) -> None:
        """
        Updates Harry's coordinates, given that he's on the lift.
        It's fairly easy! ;)
        """
        # work out new position
        self.y += self.dy
        return

    def check_lift_fall(self):
        """
        This function tests to see if harry has walked off the edge of a lift.
        By the time this function is called, x and y will have been updated,
        but rect won't have as we haven't called draw() yet...
        """
        pt = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + 1
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
            self.on_lift = False
            self.state = STATE.FALLING
            self.dx = 0
            self.dy = config.harry_falling_hy_velocity
            self.fall.play()

        return True

    def check_edge_falling(self):
        """
        This function tests to see if harry has walked off the edge of a floor tile.
        """
        fall = False
        pt = utils.tile_to_real(self.tx, self.ty + 1)
        element = next(iter([r for r in self.level.all_landables() if r.rect.collidepoint(pt)]), None)
        if not element or (element.name != 'floor' and element.name != 'ladder'):
            if utils.left_edge_of_block(self.x):
                fall = True

        if fall:
            self.state = STATE.FALLING
            self.dx = 0
            self.dy = config.harry_falling_hy_velocity
            self.fall.play()
        return

    def process_move(self) -> None:
        """
        If we're moving, the speed (dx, dy values) and direction will have
        been updated by the keypress handlers above.  So we need to check if
        we can make the move, before updating the x,y co-ordinates.
        """
        if self.dx != 0:
            if self.check_can_move_sideways() or self.on_lift:
                self.state = STATE.WALKING
                self.x += self.dx
            else:
                self.state = STATE.STILL
                self.dx = 0

            # did he walk off the edge ...?
            if self.on_lift:
                self.check_lift_fall()
            else:
                self.check_edge_falling()

        if self.dy != 0 and not self.on_lift and self.state != STATE.FALLING and self.state != STATE.JUMP:
            if self.check_can_move_up_down():
                self.state = STATE.WALKING
                self.y += self.dy
            else:
                self.state = STATE.STILL
                self.dy = 0

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
        True for all's OK, or
        False for not OK (i.e. we've splatted).
        """
        # if we're not falling update Harry's state based on keys pressed
        if self.state != STATE.FALLING:
            self.update_based_on_controls(ctrls)

        if self.dx == 0 and self.dy == 0:
            return True

        # if we're on the lift, update the y position.
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

        # check we didn't fall or jump out of the level!
        if self.level.is_outside_playable_area(self):
            self.state = STATE.SPLAT
            return False

        # check for any consumables!
        pt = self.rect.centerx, self.rect.y + config.tile_height
        element = next(iter([r for r in self.level.elements if r.rect.collidepoint(pt)]), None)
        if element and element.name == 'egg':
            self.level.consume_egg(element)
            self.egg.play()
        if element and element.name == "grain":
            self.level.consume_grain(element)
            self.grain.play()
        return True
