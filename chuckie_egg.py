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
            window.blit(text_surface, (300, 480))
            x = 300 + text_surface.get_width() + 20

        if take_input:
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


scores = [('Nigel A.', 198300), ('A&F', 80000), ('A&F', 70000), ('A&F', 60000),
            ('A&F', 50000), ('A&F', 40000), ('A&F', 30000), ('A&F', 20000),
            ('A&F', 10000), ('nerdSezzer', 5000)]


def get_high_scores():
    global scores
    return scores


def update_high_scores(new_name, new_score):
    global scores
    for name, score in get_high_scores():
        if new_score > score:
            x = scores.index((name, score))
            n = scores[:x]
            n.append((new_name, new_score))
            n += scores[x:-1]
            scores = n
    return


def high_scores_screen():
    while ctrls.paused:
        time.sleep(0.05)
        window.fill([0, 0, 0])
        title_font = pygame.font.Font(os.path.join('.', config.font_name), 72)
        text_surface = title_font.render("CHUCKIE EGG", False, pygame.color.Color('yellow'))
        x = (config.window_width - text_surface.get_width()) // 2
        y = 120
        window.blit(text_surface, (x, y))
        y += text_surface.get_height()

        sub_title_font = font
        text_surface = sub_title_font.render("HIGH SCORES", False, pygame.color.Color('yellow'))
        x = (config.window_width - text_surface.get_width()) // 2
        y += 20
        window.blit(text_surface, (x, y))
        y += text_surface.get_height()

        y += 40
        scores = get_high_scores()
        for name, score in scores:
            index = scores.index((name, score))
            text_surface = sub_title_font.render(f"{index+1}", False, pygame.color.Color('green'))
            window.blit(text_surface, (440, y))
            text_surface = sub_title_font.render(f"{score}", False, pygame.color.Color('green'))
            window.blit(text_surface, (620-text_surface.get_width(), y))
            text_surface = sub_title_font.render(name, False, pygame.color.Color('green'))
            window.blit(text_surface, (640, y))
            y += text_surface.get_height()
            y += 10

        start_one = font
        text_surface = start_one.render("Press S to start", False, pygame.color.Color('yellow'))
        x = (config.window_width - text_surface.get_width()) // 2
        y += 40
        window.blit(text_surface, (x, y))

        pygame.display.flip()
        clock.tick(fps)
        ctrls.process_events(None)

    pygame.mixer.Sound.play(start)
    return

# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------


pygame.time.set_timer(ctrls.HALF_SECOND_TICK, 500)

all_done = False
tick = False

level = Level(levels[status.game_level], status)
level.create()

while not all_done:

    high_scores_screen()

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
                    update_high_scores(name, status.game_score)
                    ctrls = Controls()
                    high_scores_screen()
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


