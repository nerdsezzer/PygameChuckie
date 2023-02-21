import pygame
import pygame.midi
import time
import os

import config
from config import tile_width, tile_height, debug_display
from chuckie.controls import Controls
from chuckie.status import Status
from chuckie.level import Level
from chuckie.level_data import levels
from high_scores import HighScores


# Set up the game window
window = pygame.display.set_mode([config.window_width, config.window_height])
pygame.display.set_caption("nerdSezzer - ChuckieEgg 2023!")
pygame.init()

clock = pygame.time.Clock()

if debug_display:
    """
    Screen width=1280, height=960
    tile width=52, height=32
    """
    print(f"Screen width={window.get_width()}, height={window.get_height()}")
    print(f"tile width={tile_width}, height={tile_height}")

status = Status()
ctrls = Controls()
high_scores = HighScores(window, clock)

pygame.mixer.init()
opps = pygame.mixer.Sound(os.path.join('.', 'opps.wav'))


# -----------------------------------------------------------------------------
# Util functions
# -----------------------------------------------------------------------------

def get_ready_screen():
    delay = 40
    font = pygame.font.Font(os.path.join('.', config.font_name), 36)
    window.fill([0, 0, 0])
    while delay:
        time.sleep(0.05)

        text_surface = font.render("Get Ready", False, pygame.color.Color('yellow'))
        x = (window.get_width()-text_surface.get_width()) // 2
        window.blit(text_surface, (x, 420))

        text_surface = font.render("Player 1", False, pygame.color.Color('cyan'))
        x = (window.get_width()-text_surface.get_width()) // 2
        window.blit(text_surface, (x, 480))

        delay -= 1
        pygame.display.flip()
        clock.tick(config.fps)
    return


# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------

# Use a time to ensure more accurate ticks for the game time.
pygame.time.set_timer(ctrls.HALF_SECOND_TICK, 500)

tick = False

# create level one.
level = Level(levels[status.game_level], status)
level.create()

# display the high scores, and wait for the 'S' key to start.
high_scores.display()

while status.game_lives > 0:

    ctrls.process_events(status.time_tick)
    if not ctrls.paused:

        # update level's movables
        tick = level.update_hens(tick)
        level.update_lifts()

        # update Harry's location, and check for death!
        if not level.harry.move(ctrls) \
                or level.check_lift_death() \
                or level.check_collision() \
                or status.is_time_up():

            opps.play()

            # check to see if there are any more lives left...
            # ... if so, display the 'Get Ready' screen and reset the level.
            if status.on_harry_died():
                get_ready_screen()
                level.reset()

        # check we've completed the level?
        if level.are_all_eggs_collected():
            status.end_of_level(window, level, clock)
            level.unload()

            # have we completed the game...
            status.game_level += 1
            if status.game_level >= len(levels):
                high_scores.update(status.game_score)
                status.reset_game()
            else:
                # ... or just the level?
                get_ready_screen()

            # recreate ctrls (to reset values), and create the next level.
            ctrls = Controls()
            level = Level(levels[status.game_level], status)
            level.create()

    # normal game tick,d
    window.fill([0, 0, 0])
    status.draw(window)
    level.draw(window)
    pygame.display.flip()
    clock.tick(config.fps)

# all done.
pygame.midi.quit()


