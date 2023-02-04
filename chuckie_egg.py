import turtle
import time

import config
from config import tile_width, tile_height, debug_display
from chuckie.controls import Controls
from chuckie.status import Status
from chuckie.level import Level
from chuckie.level_data import levels


# Set up the game window
window = turtle.Screen()
window.tracer(0)
window.mode("standard")
window.setup(config.window_width, config.window_height)
window.title("Sezzer's Revenge... ChuckieEgg 2023!")
window.bgcolor("black")

if debug_display:
    """
    Screen width=1280, height=960
    tile width=53, height=32
    """
    print(f"Screen width={window.window_width()}, height={window.window_height()}")
    print(f"tile width={tile_width}, height={tile_height}")

# Ok, lets do this...
status = Status()
ctrls = Controls()
ctrls.register_handlers(window)
level = Level(levels[status.game_level], status)
level.draw()


# -----------------------------------------------------------------------------
# Util functions
# -----------------------------------------------------------------------------


def play_music():
    delay = 40  # 2 seconds
    while delay:
        time.sleep(0.05)
        window.update()
        delay -= 1

# -----------------------------------------------------------------------------
# main loop
# -----------------------------------------------------------------------------


all_done = False
tick = False

while not all_done:

    while status.game_lives > 0:

        while ctrls.paused:
            time.sleep(0.05)
            window.update()

        tick = not tick
        if tick:
            for hen in level.hens:
                hen.move()

        for lift in level.lifts:
            lift.move()

        if not level.harry.move(ctrls) \
                or level.check_lift_death() \
                or level.check_collision() \
                or status.is_time_up():
            print("Oopsie!")
            status.game_lives -= 1
            play_music()          # or stall for 2 seconds
            level.reset()

        if level.are_all_eggs_collected():
            print("Yay!")
            # copy bonus to score
            # update lives (10,000 = 1 life).
            status.update_score_end_of_level(window)

            # scene change / next level
            level.unload()

            # stall for a bit...
            play_music()

            status.game_level += 1
            if status.game_level >= len(levels):
                all_done = True
                break

            # recreate Level with the next lot of game data.
            level = Level(levels[status.game_level], status)
            level.draw()
            break

        # normal game tick,
        status.update(level.harry, level.hens)
        time.sleep(0.03)
        window.update()

    # ah, sad face...
    if status.game_lives == 0:
        print("game over!")
        break

turtle.done()


