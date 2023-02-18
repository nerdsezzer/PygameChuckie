import config
from config import tile_width, tile_height


def snap_to_tile(x, y):
    adj_x = (x // tile_width) * tile_width
    adj_y = (y // tile_height) * tile_height
    return adj_x, adj_y


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


def top_of_block(real_y):
    return not real_y % config.tile_height


def middle_of_block(real_x):
    return not real_x % config.tile_width

def center_of_tile(real_x):
    return (real_x % config.tile_width) == config.tile_width//2

def is_outside_playable_area(thing):
    return thing.x > config.right_limit \
           or thing.x < config.left_limit \
           or thing.y > config.top_limit \
           or thing.y < config.bottom_limit
