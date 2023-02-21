
#
# display settings.
#
window_width = 1280
window_height = 960

fps = 20

x_tiles = 22
y_tiles = 22

#
# normally equate to tile_width = 52, tile_height = 32
#
tile_width = 52
tile_height = 32

#
# screen limits
#
left_limit = 0*tile_width
right_limit = 22*tile_width
bottom_limit = 0*tile_height
top_limit = 28*tile_height      # note this one is +4'd to allow Harry to jump and come back!

#
# "physics" values
#
jump_height = 0 - (13 + 4)
gravity = 4

#
# default speeds and limits
#
harry_hx_velocity = tile_width / 4
harry_default_hy_velocity = tile_height / 2
harry_falling_hy_velocity = tile_height
max_fall_velocity = tile_height/2

hen_hx_velocity = tile_width / 4
hen_hy_velocity = tile_height / 2

lift_hy_velocity = 0 - (tile_height / 6)

#
# the font for all text...
#
font_name = "bedstead.otf"

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
# settings to support debug...
#
start_paused = False

#
# settings to support debug...
#
debug_display = False
debug_harry = False
debug_hens = False
debug_lifts = False

#
# zero based index for level to load
#
starting_level = 0
