import pygame
import pygame.midi
import time
import threading
import sys

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
status = Status(window)
ctrls = Controls()
level = Level(levels[status.game_level], status)
level.draw()


# -----------------------------------------------------------------------------
# Util functions
# -----------------------------------------------------------------------------


def get_ready_screen():
    delay = 40
    while delay:
        # print(delay)
        time.sleep(0.05)
        window.fill([0, 0, 0])
        text_surface = status._font.render("Get Ready", False, pygame.color.Color('yellow'))
        window.blit(text_surface, (550, 420))
        text_surface = status._font.render("Player 1", False, pygame.color.Color('cyan1'))
        window.blit(text_surface, (565, 480))
        pygame.display.flip()
        clock.tick(fps)
        delay -= 1
    return

# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------


sounds = SoundsThread()
sounds.start()

all_done = False
tick = False

while not all_done:

    while status.game_lives > 0:

        ctrls.process_events()

        if not ctrls.paused:

            tick = not tick
            if tick:
                for hen in level.hens:
                    hen.move()

            for lift in level.lifts:
                lift.move()

            if not level.harry.move(ctrls, sounds) \
                    or level.check_lift_death() \
                    or level.check_collision() \
                    or status.is_time_up():
                print("Oopsie!")
                status.game_lives -= 1
                # or stall for 2 seconds
                get_ready_screen()
                level.reset()

            if level.are_all_eggs_collected():
                print("Yay!")
                # copy bonus to score and update lives (10,000 = 1 life).
                status.update_score_end_of_level(window)

                # scene change / next level
                level.unload()

                # stall for a bit...
                get_ready_screen()

                status.game_level += 1
                if status.game_level >= len(levels):
                    all_done = True
                    break

                # recreate Level with the next lot of game data.
                level = Level(levels[status.game_level], status)
                level.draw()
                break

            status.update()

        # normal game tick,d
        window.fill([0, 0, 0])
        status.draw(level.harry, level.hens)
        level.elements.draw(window)
        level.hens.draw(window)
        level.lifts.draw(window)
        level.harrys.draw(window)
        pygame.display.flip()
        clock.tick(fps)

    # ah, sad face...
    if status.game_lives == 0:
        print("game over!")
        break


print("bye!")
del sounds.player
pygame.midi.quit()


