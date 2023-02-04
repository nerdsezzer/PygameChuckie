
#
# display settings.
#
window_width = 1280
window_height = 960

x_tiles = 22
y_tiles = 22

#
# normally equate to tile_width = 52, tile_height = 32
#
tile_width = int(window_width / (x_tiles+2))
tile_height = int(window_height / (y_tiles+8))

#
# screen limits
#
left_limit = -11*tile_width
right_limit = 10*tile_width
bottom_limit = -12*tile_height
top_limit = 14*tile_height                  # note this one is +4'd to allow Harry to jump and come back!
top_limit_for_lift = 28*tile_height         # this is where the lift disappears, to respawn at the bottom.

#
# global width and height values for drawing the tiles/sprites.
#
global_w = 5
global_h = 3

#
# "physics" values
#
jump_height = 15 + 4
gravity = 4

#
# default speeds and limits
#
harry_default_hx_velocity = tile_width / 4
harry_default_hy_velocity = tile_height / 2
harry_falling_hy_velocity = tile_height
max_fall_velocity = 0-tile_height/2

hen_default_hx_velocity = tile_width / 4
hen_default_hy_velocity = tile_height / 2

lift_default_hy_velocity = tile_height / 4

#
# make_it_easy, setting this to True means the level is won,
# just picking up on egg, will complete the level
#
make_it_easy = False

#
# hens_are_friendly, setting this to True makes the walking hens
# safe, Harry can run through them.
#
hens_are_friendly = False

#
# hens_are_jumpable...
#
hens_are_jumpable = True

#
# settings to support debug...
#
start_paused = True
debug_display = True
debug_harry = False
debug_hens = True
debug_lifts = False

#
# zero based index for level to load
#
starting_level = 2
