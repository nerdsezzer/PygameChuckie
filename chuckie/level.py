import pygame
import os

import config
from chuckie.thing import DIR
from chuckie.hen import Hen
from chuckie.harry import Harry
from chuckie.lift import Lift
from chuckie.status import Status
import chuckie.utils as utils
from chuckie.layout_elements import Egg, Grain, Floor, Ladder


class Level:
    """
    This class manages a level in the game.  At the basic level the level
    is a two-dimensional array of tiles, each of which may contain a game
    element: a floor tile, an egg, or Harry.

    All logic about the state of the level should be contained in this
    class.  For example the number of eggs left to be collected (a win
    condition).
    """

    def __init__(self, level_data, status: Status):
        self.data = level_data
        self.status = status
        self.status.reset_new_level()
        self.tiles = {}
        self.elements = pygame.sprite.Group()
        self.handles = {}
        self._harrys = pygame.sprite.Group()
        self._harry = None
        self._hens = pygame.sprite.Group()
        self._lifts = pygame.sprite.Group()
        self.level_egg_count = 0
        self.eggs_collected = 0

        self.start = pygame.mixer.Sound(os.path.join('.', 'start.wav'))
        return

    def __repr__(self):
        return f"level={self.status.game_level}, lifts={len(self._lifts) // 2}, " \
               f"hens={len(self._hens)}, eggs collected={self.eggs_collected}/{self.level_egg_count}"

    @property
    def harry(self) -> Harry:
        return self._harry

    @staticmethod
    def grid_to_tile(a, b):
        return b + 1, a + 6

    def create(self):
        """
        Create the level based on the data passed in on the initialiser.
        Items are created as they are found.  Moving/Movable objects are
        assigned to member variables, other objects are held by handles.
        """
        for a in reversed(range(0, config.y_tiles)):
            for b in reversed(range(0, config.x_tiles)):
                element = self.data[a][b]
                (x, y) = Level.grid_to_tile(a, b)

                handle = None
                label = None

                if element == 'e':
                    handle, label = (Egg(x, y), "egg")
                    self.level_egg_count += 1
                elif element == 'g':
                    handle, label = (Grain(x, y), "grain")
                elif element == 'l':
                    handle, label = (Ladder(x, y), "ladder")
                elif element == 'f':
                    handle, label = (Floor(x, y), "floor")
                elif element == 'hl':
                    self._hens.add(Hen(self, x-1, y, DIR.LEFT))
                elif element == 'hr':
                    self._hens.add(Hen(self, x-1, y, DIR.RIGHT))
                elif element == 'cl':
                    self._harry = Harry(self, x, y, DIR.LEFT)
                    self._harrys.add(self._harry)
                elif element == 'cr':
                    self._harry = Harry(self, x, y, DIR.RIGHT)
                    self._harrys.add(self._harry)
                elif element == '-l':
                    self._lifts.add(Lift(self, x, y, DIR.LEFT))
                elif element == '-r':
                    self._lifts.add(Lift(self, x, y, DIR.RIGHT))

                if handle:
                    self.elements.add(handle)
                    self.handles[(x, y)] = handle
                if label:
                    self.tiles[(x, y)] = label

            self.play_start_sound()
        return

    def play_start_sound(self):
        self.start.play()
        self.start.set_volume(0.5)
        return

    def all_landables(self):
        return self._lifts.sprites() + self.elements.sprites()

    def update_hens(self, tick: bool):
        hen: Hen
        if tick:
            for hen in self._hens:
                hen.move()
        return not tick

    def update_lifts(self):
        lift: Lift
        for lift in self._lifts:
            lift.move()
        return

    def draw(self, display: pygame.display):
        self.elements.draw(display)
        self._hens.draw(display)
        self._lifts.draw(display)
        self._harrys.draw(display)
        return

    def reset(self):
        """
        Called when Harry has died.
        This puts the moveable objects back to their starting positions,
        and updates the status.
        """
        self._reset_moveables()
        self.status.reset_time()
        self.play_start_sound()
        return

    def unload(self):
        """
        Called when a level has been completed.
        Clear and delete all sprite objects, moveable and otherwise.
        """
        self._unload_moveables()

        for handle in self.handles.values():
            handle.kill()
            del handle
        return

    def _unload_moveables(self):
        """
        Clear and delete all the moveable things, as needed when a level
        is reset.
        """
        for x in self._harrys:
            x.kill()
            del x

        del self._harry

        for hen in self._hens:
            hen.kill()
            del hen

        for lift in self._lifts:
            lift.kill()
            del lift
        return

    def _reset_moveables(self):
        """
        Clear, delete and then recreate the movables:
           Harry, the hens and the lifts.
        """
        self._unload_moveables()

        self._harrys = pygame.sprite.Group()
        self._hens = pygame.sprite.Group()
        self._lifts = pygame.sprite.Group()

        for a in reversed(range(0, 22)):
            for b in reversed(range(0, 22)):
                element = self.data[a][b]
                x, y = Level.grid_to_tile(a, b)

                if element == 'hl':
                    self._hens.add(Hen(self, x, y, DIR.LEFT))
                elif element == 'hr':
                    self._hens.add(Hen(self, x, y, DIR.RIGHT))
                elif element == 'cl':
                    self._harry = Harry(self, x, y, DIR.LEFT)
                    self._harrys.add(self._harry)
                elif element == 'cr':
                    self._harry = Harry(self, x, y, DIR.RIGHT)
                    self._harrys.add(self._harry)
                elif element == '-l':
                    self._lifts.add(Lift(self, x, y, DIR.LEFT))
                elif element == '-r':
                    self._lifts.add(Lift(self, x, y, DIR.RIGHT))
        return

    # -------------------------------------------------------------------------
    # Win condition - Egg related
    # -------------------------------------------------------------------------

    def consume_egg(self, _egg):
        """
        Add 100 points to the score, increment count of eggs collected,
        then delete the egg object from the list of handles and elements.
        """
        self.status.update_egg_collected()
        self.eggs_collected += 1
        (tx, ty) = utils.real_to_tile(_egg.rect.x, _egg.rect.y)
        egg = self.handles[(tx, ty)]
        egg.kill()
        self.elements.remove(egg)
        del egg
        del self.handles[(tx, ty)]
        del self.tiles[(tx, ty)]
        return

    def consume_grain(self, _grain, hen_mode=False):
        """
        Add 50 points to the score, and stall time ticking down if Harry
        found the grain.
        Then delete the grain object from the list of handles and elements.
        """
        if not hen_mode:
            self.status.update_grain_collected()
        (tx, ty) = utils.real_to_tile(_grain.rect.x, _grain.rect.y)
        grain = self.handles[(tx, ty)]
        grain.kill()
        self.elements.remove(grain)
        del grain
        del self.handles[(tx, ty)]
        del self.tiles[(tx, ty)]
        return

    def are_all_eggs_collected(self):
        """
        If all the eggs have been collected, level is completed successfully.
        """
        if config.make_it_easy and self.eggs_collected > 0:
            return True
        return self.level_egg_count == self.eggs_collected

    # -------------------------------------------------------------------------
    # Life Lost condition - Hen collision
    # -------------------------------------------------------------------------

    def check_collision(self) -> bool:
        """
        Check to see if harry and a hen have collided.  If so, end of life. :(
        This is called 'after' move() functions, so x and y have been updated
        and draw() as been called.
        Note: tile_width = 52, tile_height = 32
        """
        if config.hens_are_friendly:
            return False

        hr = self.harry.rect.copy()
        hr.y += config.tile_height//2
        hr.height -= config.tile_height//2
        for h in self._hens:
            r = pygame.Rect(h.rect.x+config.tile_width+13,
                            h.rect.y,
                            config.tile_width-26,
                            (config.tile_height*2))
            if hr.colliderect(r):
                return True
        return False

    # -------------------------------------------------------------------------
    # Life Lost condition - on lift at top of screen - squished.
    # -------------------------------------------------------------------------

    def check_lift_death(self) -> bool:
        """
        Check to see if harry was on a lift that just 'disappeared' at the top
        of the screen.  If so, he's lost a life. :(
        """
        if not self.harry.on_lift:
            return False

        if self.harry.rect.y < Lift.LIFT_DISAPPEARS_AT - (2*config.tile_height):
            return True

        return False

    # -------------------------------------------------------------------------
    # General level navigation support...
    # -------------------------------------------------------------------------

    def element_at(self, tx, ty) -> str:
        pt = utils.tile_to_real(tx, ty)
        element = next(iter([r.name for r in self.all_landables() if r.rect.collidepoint(pt)]), None)
        return element

    @staticmethod
    def is_outside_playable_area(thing):
        return thing.x > config.right_limit \
               or thing.x < config.left_limit \
               or thing.y > config.top_limit \
               or thing.y < config.bottom_limit
