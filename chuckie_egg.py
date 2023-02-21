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
clock = pygame.time.Clock()
pygame.init()
fps = 20

font = pygame.font.Font(os.path.join('.', config.font_name), 36)

if debug_display:
    """
    Screen width=1280, height=960
    tile width=52, height=32
    """
    print(f"Screen width={window.get_width()}, height={window.get_height()}")
    print(f"tile width={tile_width}, height={tile_height}")

# Ok, lets do this...
status = Status(font)
ctrls = Controls()
high_scores = HighScores()

pygame.mixer.init()
opps = pygame.mixer.Sound(os.path.join('.', 'opps.wav'))
start = pygame.mixer.Sound(os.path.join('.', 'start.wav'))


# -----------------------------------------------------------------------------
# Util functions
# -----------------------------------------------------------------------------

def _screen(text_one: str, text_two: str = None, take_input: bool = False):
    delay = 40
    name = ""

    window.fill([0, 0, 0])
    while delay:
        time.sleep(0.05)

        text_surface = font.render(text_one, False, pygame.color.Color('yellow'))
        x = (window.get_width()-text_surface.get_width()) // 2
        window.blit(text_surface, (x, 420))

        if text_two:
            text_surface = font.render(text_two, False, pygame.color.Color('cyan'))
            x = 300 if take_input else (window.get_width()-text_surface.get_width()) // 2
            window.blit(text_surface, (x, 480))

        if take_input:
            x = 300 + text_surface.get_width() + 20
            key = ctrls.process_events_for_input()
            if key:
                if key == -1:
                    take_input = False
                    name = ""
                elif key == -2:
                    take_input = False
                else:
                    text_surface = font.render(name, False, pygame.color.Color('black'))
                    window.blit(text_surface, (x, 480))
                    name += key
                    text_surface = font.render(name, False, pygame.color.Color('white'))
                    window.blit(text_surface, (x, 480))
        else:
            delay -= 1

        pygame.display.flip()
        clock.tick(fps)
    return name


def get_ready_screen():
    return _screen("Get Ready", "Player 1")


def oh_dear_screen():
    return _screen("Game Over")


def all_done_screen():
    return _screen("Well Done", "Please enter your name:", True)


# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------


pygame.time.set_timer(ctrls.HALF_SECOND_TICK, 500)

all_done = False
tick = False

level = Level(levels[status.game_level], status)
level.create()

while not all_done:

    high_scores.high_scores_screen(ctrls, window, font, clock, fps)
    pygame.mixer.Sound.play(start)

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

                pygame.mixer.Sound.play(opps)
                if not status.on_harry_died():
                    break

                # or stall for 2 seconds
                get_ready_screen()
                level.reset()
                pygame.mixer.Sound.play(start)

            # check we've completed the level?
            if level.are_all_eggs_collected():
                status.update_score_end_of_level(window, level, clock, fps)
                level.unload()

                # have we completed the game?
                status.game_level += 1
                if status.game_level >= len(levels):
                    name = all_done_screen()
                    high_scores.update_high_scores(name, status.game_score)
                    ctrls = Controls()
                    high_scores.high_scores_screen(ctrls, window, font, clock, fps)
                    pygame.mixer.Sound.play(start)
                    status.game_level = 0
                else:
                    # stall for a bit...
                    get_ready_screen()

                # recreate Level with the next lot of game data.
                level = Level(levels[status.game_level], status)
                level.create()
                pygame.mixer.Sound.play(start)
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

pygame.midi.quit()


