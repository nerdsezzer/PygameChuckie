import config
from config import tile_width, tile_height


def tile_to_real(x, y):
    real_x = x * tile_width
    real_y = y * tile_height
    return real_x, real_y


def real_to_tile(real_x, real_y):
    remainder = real_x % tile_width
    x = int(real_x / tile_width)
    if real_x < 0 and remainder:
        x -= 1

    remainder = real_y % tile_height
    y = int(real_y / tile_height)
    if real_y > 0 and remainder:
        y += 1
    return x, y


def real_x_to_tile(real_x) -> (int, str):
    """ Returns the tx value and 'p' if its partially in the tile, or 'f' for fully in the tile. """
    remainder = real_x % tile_width
    x = int(real_x / tile_width)
    return x, "p" if remainder else "f"


def real_y_to_tile(real_y):
    remainder = real_y % tile_height
    y = int(real_y / tile_height)
    return y, "p" if remainder else "f"


def top_of_block(real_y):
    return not real_y % config.tile_height


def middle_of_block(real_x):
    return not real_x % config.tile_width


def is_outside_playable_area(thing):
    return thing.hx > config.right_limit \
        or thing.hx < config.left_limit \
        or thing.hy > config.top_limit \
        or thing.hy < config.bottom_limit
