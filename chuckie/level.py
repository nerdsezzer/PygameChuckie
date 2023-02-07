import pygame
import config
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
        self.harrys = pygame.sprite.Group()
        self.hens = pygame.sprite.Group()
        self.lifts = pygame.sprite.Group()
        self.level_egg_count = 0
        self.eggs_collected = 0
        return

    @property
    def harry(self):
        return self.harrys.sprites()[0]

    @staticmethod
    def grid_to_tile(a, b):
        return b + 1, a + 6

    def draw(self):
        """
        Create the level based on the data passed in on the initialiser.
        Items are created as they are found.  Moving/Movable objects are
        assigned to member variables.
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
                    self.hens.add(Hen('hen', self, x, y, "left"))
                elif element == 'hr':
                    self.hens.add(Hen('hen', self, x, y, "right"))
                elif element == 'cl':
                    self.harrys.add(Harry(self, x, y, "left"))
                elif element == 'cr':
                    self.harrys.add(Harry(self, x, y, "right"))
                elif element == '-l':
                    self.lifts.add(Lift(self, x, y, "left"))
                elif element == '-r':
                    self.lifts.add(Lift(self, x, y, "right"))
                #else:
                #    if config.debug_display:
                #        draw_box(x, y, "DarkSlateGray")

                if handle:
                    self.elements.add(handle)
                    self.handles[(x, y)] = handle
                if label:
                    self.tiles[(x, y)] = label
        return

    def reset(self):
        """
        This puts Harry and the Hens back to their starting positions.
        and updates the status.
        """
        self._reset_harry_and_hens()
        self.status.reset_time()
        return

    def unload(self):
        """
        Clear and delete all the turtle objects.
        """
        # clear and delete the moving things (harry and the hens)
        self.unload_movers()

        # ... then clear and delete all the other elements in the level
        for handle in self.handles.values():
            handle.kill()
            del handle
        return

    def unload_movers(self):
        """
        Clear and delete all the moveable things, as needed when a level
        is reset.
        """
        self.harry.kill()
        #del self.harry

        for hen in self.hens:
            hen.kill()
            del hen

        for lift in self.lifts:
            lift.kill()
            del lift
        return

    def _reset_harry_and_hens(self):
        """
        Clear, delete and then recreate the movables:
           Harry, the hens and the lifts.
        """
        self.unload_movers()
        self.harrys = pygame.sprite.Group()
        self.hens = pygame.sprite.Group()
        self.lifts = pygame.sprite.Group()

        for a in reversed(range(0, 22)):
            for b in reversed(range(0, 22)):
                element = self.data[a][b]
                (x, y) = Level.grid_to_tile(a, b)

                if element == 'hl':
                    self.hens.add(Hen('hen', self, x, y, "left"))
                elif element == 'hr':
                    self.hens.add(Hen('hen', self, x, y, "right"))
                elif element == 'cl':
                    self.harrys.add(Harry(self, x, y, "left"))
                elif element == 'cr':
                    self.harrys.add(Harry(self, x, y, "right"))
                elif element == '-l':
                    self.lifts.add(Lift(self, x, y, "left"))
                elif element == '-r':
                    self.lifts.add(Lift(self, x, y, "right"))
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
        @Todo, this might be a bit forgiving as it only checks top/head tile.
        """
        if config.hens_are_friendly:
            return False

        harry_tx, harry_ty = utils.real_to_tile(self.harry.rect.x, self.harry.rect.y)
        for h in self.hens:
            tx, ty = utils.real_to_tile(h.rect.x, h.rect.y)
            if harry_tx == tx and harry_ty == ty:
                return True
            if not config.hens_are_jumpable and harry_tx == tx and harry_ty-1 == ty:
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

        if self.harry.rect.y > config.top_limit_for_lift + config.tile_height:
            return True

        return False

    # -------------------------------------------------------------------------
    # General level navigation support...
    # -------------------------------------------------------------------------

    def get(self, tx, ty) -> str:
        if (tx, ty) not in self.tiles:
            return ""
        else:
            return self.tiles[(tx, ty)]
