"""
This module contains the Harry class, which represents the main
playable character - Hen-House Harry.
"""
import os

import pygame

import chuckie.utils as utils
import config
from chuckie.controls import Controls
from chuckie.thing import Thing, DIR, STATE
from config import gravity, tile_width, jump_height


class Harry(Thing):
    """
    This module provides logic for the main playable character: Hen House Harry.

    He is a two tile high character, that has two sets of sprite images; one for
    going left-right and one for up-down.

    Harry is the only character whose direction is controlled by the user, and
    who is able to jump / fall.

    Harry can consume both eggs and grain.  Both award points, but the grain
    stalls the game time from ticking down.
    """
    def __init__(self, level, start_tile_x: int, start_tile_y: int, start_direction: DIR):
        super().__init__('harry', level, start_tile_x, start_tile_y, start_direction)

        self.images_left_right = []
        self.images_up_down = []
        self.image = self._load_images(os.path.join('.', 'images', 'harry-debug.png'))
        self.init_rect(self.image, start_tile_x, start_tile_y)

        self.step = pygame.mixer.Sound(os.path.join('.', 'resources', 'step.wav'))
        self.jump = pygame.mixer.Sound(os.path.join('.', 'resources', 'jump.wav'))
        self.fall = pygame.mixer.Sound(os.path.join('.', 'resources', 'fall.wav'))
        self.egg = pygame.mixer.Sound(os.path.join('.', 'resources', 'egg.wav'))
        self.grain = pygame.mixer.Sound(os.path.join('.', 'resources', 'grain.wav'))
        self.ladder = pygame.mixer.Sound(os.path.join('.', 'resources', 'ladder.wav'))

        if config.debug_harry:
            print(f"putting harry at [{start_tile_x}, {start_tile_y}]")

        self.state = STATE.STILL
        self.on_lift = False

        self.draw()
        return

    def _load_images(self, file: str):
        for i in range(1, 5):
            if not config.debug_display:
                file = os.path.join('.', 'images', 'harry-' + str(i) + '.png')
            img = pygame.image.load(file).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_left_right.append(img)

        for i in range(1, 5):
            if not config.debug_display:
                file = os.path.join('.', 'images', 'harry-ladder-' + str(i) + '.png')
            img = pygame.image.load(file).convert()
            img.convert_alpha()
            img.set_colorkey((0, 0, 0))
            self.images_up_down.append(img)

        return self.images_left_right[0]

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
                if self.is_going_right():
                    # only play the step noise, if Harry is actually moving.
                    # if he moves sideways on the lift, his state is set to WALKING.
                    self.step.play()
                self.image = self.images_left_right[self.frame]
            elif self.direction == DIR.LEFT:
                if self.is_going_left():
                    # see comment above.
                    self.step.play()
                self.image = pygame.transform.flip(self.images_left_right[self.frame], True, False)
            elif (self.direction == DIR.UP or self.direction == DIR.DOWN) and self.dy != 0:
                self.ladder.play()
                self.image = self.images_up_down[self.frame]
            else:
                by_deltas()
        return

    def update_based_on_controls(self, ctrls: Controls) -> None:
        """
        Figure out what the dx and dy values should be given what
        keys are pressed.
        """
        if self.state == STATE.JUMP:
            # this fixes the 'double(buffered) jump' bug...
            # also needed in pygame version.
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

    def get_possible_moves(self):
        """
        Returns a list of bools, that denote if Harry can go
        up, down, left or right, in that order.
        """
        moves = [False, False, False, False]

        items = self.level.all_landables()
        above_tile = utils.tile_to_real(self.tx, self.ty-2)
        above_tile_element = next(iter([r.name for r in items
                                        if r.rect.collidepoint(above_tile)]), "")

        current_tile = utils.tile_to_real(self.tx, self.ty)
        current_element = next(iter([r.name for r in items if
                                     r.rect.collidepoint(current_tile)]), "")

        under_foot = utils.tile_to_real(self.tx, self.ty+1)
        under_foot_element = next(iter([r.name for r in items
                                        if r.rect.collidepoint(under_foot)]), "")

        left = utils.tile_to_real(self.tx-1, self.ty)
        left_element = next(iter([r.name for r in items
                                  if r.rect.collidepoint(left)]), "")

        under_left = utils.tile_to_real(self.tx-1, self.ty+1)
        under_left_element = next(iter([r.name for r in items
                                        if r.rect.collidepoint(under_left)]), "")

        right = utils.tile_to_real(self.tx+1, self.ty)
        right_element = next(iter([r.name for r in items
                                   if r.rect.collidepoint(right)]), "")

        under_right = utils.tile_to_real(self.tx+1, self.ty+1)
        under_right_element = next(iter([r.name for r in items
                                         if r.rect.collidepoint(under_right)]), "")

        def not_landable(element):
            return element == "" or element == 'grain' or element == 'egg'

        # allow go-up if above tile is a ladder
        if above_tile_element == 'ladder':
            moves[0] = True

        # allow go-down if the underneath tile is a ladder.
        if under_foot_element == 'ladder':
            moves[1] = True

        # if we're on a ladder, moving sideways isn't allowed, unless we're on
        # a landable-ladder tile (i.e. one flanked by 'floor' tiles).
        if current_element == 'ladder':
            if under_left_element == 'floor':
                moves[2] = True
            if under_right_element == 'floor':
                moves[3] = True

            if under_left_element == 'floor' and not_landable(under_right_element):
                moves[3] = True
            if under_right_element == 'floor' and not_landable(under_left_element):
                moves[2] = True
        else:
            # if we're not on a ladder, so we can go left or right unless
            # there's a step in the way.
            moves[2] = True
            moves[3] = True
            if left_element == 'floor':
                moves[2] = False
            if right_element == 'floor':
                moves[3] = False

        return moves

    def check_can_move_sideways(self) -> bool:
        """
        Checks to see if a sideways move is possible, i.e. there is a floor or
        ladder to step on.

        First it checks to see if Harry is moving out of the playable area, if so
        the move is stopped.

        If Harry is just moving within a tile, i.e. he's not on the left edge
        of a tile, then allow the move.

        Otherwise, if Harry is standing on top of a tile, calculate the
        possible moves.

        :return: True for move can be made, False otherwise.
        """
        # stop if we reach either the left or right edge of playable area.
        if self.rect.centerx + self.dx < config.left_edge \
                or self.rect.centerx + self.dx > config.right_edge:
            self.state = STATE.STILL
            self.dx = 0
            return False

        # if this is just a 'within tile move' then crack on...
        if self.x % tile_width:
            return True

        # if we're not on the top of a tile, we can't go sideways.
        if utils.top_of_block(self.y):
            moves = self.get_possible_moves()
            if self.is_going_left() and moves[DIR.LEFT.value]:
                return True
            if self.is_going_right() and moves[DIR.RIGHT.value]:
                return True
        return False

    def check_can_move_up_down(self) -> bool:
        """
        Checks to see if a move up or down is possible, i.e. we're on or about
        to get on a ladder.

        If Harry is not on a tile boundary, then just allow the up/down move to
        happen.  We only need to decided if a move is possible when he's aligned
        with the grid (i.e. on top and left edge of a tile).

        :return: True for move can be made, False otherwise.
        """
        # if this is just a 'within tile move' then crack on...
        if self.y % config.tile_height:
            return True

        # if we're not on the left-edge of a tile, we can't go up or down.
        if utils.left_edge_of_block(self.x):
            moves = self.get_possible_moves()
            if self.is_going_up() and moves[DIR.UP.value]:
                return True
            if self.is_going_down() and moves[DIR.DOWN.value]:
                return True
        return False

    def _snap(self, obj) -> None:
        """
        Used to update Harry's co-ordinates.  Sets x to the target position,
        and y so that Harry is standing on the tile passed in.
        This function leaves Harry in the 'STILL' state.
        :param obj: the tile Harry collided with, that we want to stand on top of.
        """
        self.x = self.x + self.dx
        self.y = obj.rect.top - self.rect.height
        self.state = STATE.STILL
        self.y_velocity = 0
        self.dy = 0

    def _bounce(self) -> None:
        """
        Used to update Harry's co-ordinates and direction, when he bounces off
        either the side of a floor tile or the edge of the screen.
        """
        self.dx = 0 - self.dx
        self.x += self.dx
        self.y += self.dy

    def process_fall(self) -> None:
        """
        Updates Harry's coordinates, given that he is falling.  Checks to see if
        he lands on a floor tile, or a landable-ladder tile.  This also updates
        Harry's direction and deltas as necessary.

        A landable-ladder tile, is one that is flanked on either side by a floor
        tile, so can be considered 'at floor level'.

        When Harry lands on a floor or landable-ladder tile, this function
        _snap()s his y co-ordinate so that he stands nicely on top of the tile
        he just collided with.
        """
        # work out new position.
        self.y += self.dy

        # rect won't have been updated yet, as draw() hasn't been called.
        point = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + self.dy
        obj = next(iter([r for r in self.level.elements if r.rect.collidepoint(point)]), None)
        if obj and obj.name == 'floor':
            self._snap(obj)
            return

        if obj and obj.name == 'ladder':
            a, b = utils.real_to_tile(obj.rect.x, obj.rect.y)
            if self.level.element_at(a-1, b) == 'floor' or self.level.element_at(a+1, b) == 'floor':
                self._snap(obj)
        return

    def process_jump(self, w_key_down: bool, s_key_down: bool) -> None:
        """
        Updates Harry's coordinates, given that he is jumping.

        Check to see if Harry should bounce off of the screen edge or a
        floor-tile using the _bounce() function.

        Check to see if Harry is landing on a floor, landable-ladder, or lift
        tile, if he is, then _snap() his location, so that he is standing nicely
        on the top of the tile.

        Check to see if Harry can grab a ladder as he jumps past one.

        Finally, if none of those situations are occurring, simply update
        coordinates to make the move.
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

        # have we hit the edge of the screen? in which case bounce!
        if self.rect.centerx + self.dx < config.left_edge \
                or self.rect.centerx + self.dx > config.right_edge:
            self._bounce()
            return

        # have we hit the edge of a floor-tile? in which case bounce!
        midpoint = self.rect.centerx + self.dx, self.rect.centery + self.dy
        obj = next(iter([r for r in self.level.all_landables()
                         if r.rect.collidepoint(midpoint)]), None)
        if self.is_going_down() and obj and obj.name == 'floor':
            self._bounce()
            return

        # has Harry landed on a floor 'tile'?
        mid_bottom = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + self.dy
        obj = next(iter([r for r in self.level.all_landables()
                         if r.rect.collidepoint(mid_bottom)]), None)
        if self.is_going_down() and obj and obj.name == 'floor':
            self._snap(obj)
            return

        # has Harry landed on a lift?
        if self.is_going_down() and obj and obj.name == 'lift':
            self._snap(obj)
            self.on_lift = True
            self.dy = config.lift_hy_velocity
            self.dx = 0
            return

        # has Harry landed on a landable-ladder tile?
        if self.is_going_down() and obj and obj.name == 'ladder':
            a, b = utils.real_to_tile(obj.rect.x, obj.rect.y)
            if self.level.element_at(a-1, b) == 'floor' \
                    or self.level.element_at(a+1, b) == 'floor':
                self._snap(obj)
                return

        # is Harry jumping through a ladder? should he grab it?
        # for level 6, Harry needs to grab a ladder at head level.
        mid_top = self.rect.midtop[0] + self.dx, self.rect.midtop[1] + self.dy
        obj2 = next(iter([r for r in self.level.all_landables()
                          if r.rect.collidepoint(mid_top)]), None)
        if (w_key_down or s_key_down) \
                and utils.left_edge_of_block(self.x + self.dx) \
                and (obj and obj.name == 'ladder' or obj2 and obj2.name == 'ladder'):
            self.x = obj.rect.x if obj else obj2.rect.x
            self.y = obj.rect.y - self.rect.height if obj else obj2.rect.y
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
        It's fairly easy!
        """
        # work out new position
        self.y += self.dy
        return

    def _fall(self) -> None:
        """
        Used to set Harry's state to falling, whether he's walked off the
        end of a floor tile or lift.
        Call the 'fall' sound .wav here.
        """
        self.state = STATE.FALLING
        self.dx = 0
        self.dy = config.harry_falling_hy_velocity
        self.fall.play()

    def check_lift_fall(self) -> None:
        """
        This function tests to see if Harry has walked off the edge of a lift.
        By the time this function is called, x and y will have been updated,
        but rect won't have as we haven't called draw() yet...
        """
        pt = self.rect.midbottom[0] + self.dx, self.rect.midbottom[1] + 1
        lift = next(iter([r for r in self.level.all_landables()
                          if r.rect.collidepoint(pt) and r.name == 'lift']), None)
        if lift is None:
            return

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
            self._fall()

    def check_edge_falling(self) -> None:
        """
        This function tests to see if harry has walked off the edge of a floor
        tile.  By the time this function is called, x and y will have been
        updated but rect won't have as we haven't called draw() yet...
        """
        lower_tile = utils.tile_to_real(self.tx, self.ty + 1)
        tile = next(iter([r for r in self.level.all_landables()
                          if r.rect.collidepoint(lower_tile)]), None)
        if not tile or (tile.name != 'floor' and tile.name != 'ladder'):
            if utils.left_edge_of_block(self.x):
                self._fall()

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

        if self.dy != 0 and not self.on_lift \
                and self.state != STATE.FALLING and self.state != STATE.JUMP:
            if self.check_can_move_up_down():
                self.state = STATE.WALKING
                self.y += self.dy
            else:
                self.state = STATE.STILL
                self.dy = 0

    def move(self, ctrls: Controls) -> bool:
        """
        Harry has an x,y position and dx,dy direction/speeds.
        1. determine change in speed/direction from key-presses.
        2. determine if harry can make the move he's setup for.
        3. update co-ords
        4. draw Harry.
        5. check he didn't go splat ... end of screen, down hole?
        6. check for any consumables at new position.

        :param ctrls: the Controls instance, representing the keypresses.
        :return: True for all's OK, False for not OK (Harry died).
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
        element = next(iter([r for r in self.level.elements
                             if r.rect.colliderect(self.rect)]), None)
        if element and element.name == 'egg':
            self.level.consume_egg(element)
            self.egg.play()
        if element and element.name == "grain":
            self.level.consume_grain(element)
            self.grain.play()
        return True
