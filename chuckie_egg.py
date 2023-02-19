import pygame
import pygame.midi
import time

import config
from config import tile_width, tile_height, debug_display
from chuckie.controls import Controls
from chuckie.status import Status
from chuckie.level import Level
from chuckie.level_data import levels
from chuckie.sounds import SoundsThread


# Set up the game window
window = pygame.display.set_mode([config.window_width, config.window_height])
clock = pygame.time.Clock()
pygame.init()
fps = 20


if debug_display:
    """
    Screen width=1280, height=960
    tile width=52, height=32
    """
    print(f"Screen width={window.get_width()}, height={window.get_height()}")
    print(f"tile width={tile_width}, height={tile_height}")

# Ok, lets do this...
status = Status()
ctrls = Controls()
level = Level(levels[status.game_level], status)
level.create()


# -----------------------------------------------------------------------------
# Util functions
# -----------------------------------------------------------------------------

def _screen(text_one: str, text_two: str = None):
    delay = 40
    while delay:
        time.sleep(0.05)
        window.fill([0, 0, 0])
        font = pygame.font.SysFont('Arial', 36)
        text_surface = font.render(text_one, False, pygame.color.Color('yellow'))
        window.blit(text_surface, (550, 420))
        if text_two:
            text_surface = font.render(text_two, False, pygame.color.Color('cyan'))
            window.blit(text_surface, (565, 480))
        pygame.display.flip()
        clock.tick(fps)
        delay -= 1
    return


def get_ready_screen():
    return _screen("Get Ready", "Player 1")


def oh_dear_screen():
    return _screen("Game Over")


def all_done_screen():
    return _screen("Well Done")


# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------


sounds = SoundsThread()
sounds.start()

pygame.time.set_timer(ctrls.HALF_SECOND_TICK, 500)

all_done = False
tick = False

while not all_done:

    while status.game_lives > 0:

        ctrls.process_events(status.time_tick)
        if not ctrls.paused:

            # update level's movables
            tick = level.update_hens(tick)
            level.update_lifts()

            # update Harry's location, and check for death!
            if not level.harry.move(ctrls, sounds) \
                    or level.check_lift_death() \
                    or level.check_collision() \
                    or status.is_time_up():

                if not status.on_harry_died():
                    break

                # or stall for 2 seconds
                get_ready_screen()
                level.reset()

            # check we've completed the level?
            if level.are_all_eggs_collected():
                status.update_score_end_of_level(window, level, clock, fps)
                level.unload()

                # have we completed the game?
                status.game_level += 1
                if status.game_level >= len(levels):
                    all_done_screen()
                    all_done = True
                    break

                # stall for a bit...
                get_ready_screen()

                # recreate Level with the next lot of game data.
                level = Level(levels[status.game_level], status)
                level.create()
                break

        # normal game tick,d
        window.fill([0, 0, 0])
        status.draw(window)
        level.draw(window)
        pygame.display.flip()
        clock.tick(fps)

    # ah, sad face...
    if status.game_lives == 0:
        oh_dear_screen()
        break

del sounds.player
pygame.midi.quit()


