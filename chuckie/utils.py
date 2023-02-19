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


def top_of_block(real_y):
    return real_y % config.tile_height == 0


def left_edge_of_block(real_x):
    return real_x % config.tile_width == 0

