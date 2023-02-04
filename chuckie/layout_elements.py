import turtle

from config import tile_width, tile_height, global_w, global_h


def draw_floor(x: int, y: int) -> (turtle, str):
    """ Draws a 'floor' tile, comprised of three dotted lines,
        raised slightly from the bottom of the tile."""
    real_x = x * tile_width
    real_y = y * tile_height

    gap = global_w
    h = 2

    floor = turtle.Turtle()
    floor.hideturtle()
    floor.penup()

    def draw_line(f, first_width: int, level: int):
        draw_pixel(f, first_width, h, "DarkGreen", real_x, real_y - level)
        draw_pixel(f, tile_width - gap - first_width, h, "DarkGreen", real_x + first_width + gap, real_y - level)

    draw_line(floor, 20, 4)
    draw_line(floor, 4, 10)
    draw_line(floor, 12, 16)
    return floor, "floor"


def draw_ladder(x: int, y: int) -> (turtle, str):
    """ Draws a 'ladder' tile, comprised on three lines, left
    and right rail, and a rung."""
    real_x = x * tile_width
    real_y = y * tile_height

    ladder = turtle.Turtle()
    ladder.hideturtle()
    ladder.penup()

    # figure out where to locate the ladder... this x value
    # is based on where/how Harry and the Hens are drawn.
    x = real_x + (tile_width // 2) - global_w
    left_rail_x = x - (3 * global_w)
    right_rail_x = x + (4 * global_w)

    # now draw the ladder:
    ladder.color("DarkMagenta")
    ladder.pensize(1)
    draw_pixel(ladder, global_w, tile_height, "DarkMagenta", left_rail_x, real_y)
    draw_pixel(ladder, global_w, tile_height, "DarkMagenta", right_rail_x, real_y)
    draw_pixel(ladder, right_rail_x - left_rail_x, global_h, "DarkMagenta", left_rail_x, real_y - (5 * global_h))
    return ladder, "ladder"


def draw_egg(x: int, y: int) -> (turtle, str):
    """ Based on Bbc version of ChuckieEgg. """

    real_x = x * tile_width
    real_y = y * tile_height

    egg = turtle.Turtle()
    egg.hideturtle()
    egg.penup()

    # figure out the 'pixel' dimensions.
    w = global_w
    h = global_h

    # figure out where to start the draw.
    real_x = real_x + (tile_width//2) - (2 * w)
    real_y = real_y - tile_height + (6 * h)

    egg.setposition(real_x, real_y)
    egg.setheading(0)
    egg.pencolor("yellow")
    egg.fillcolor("yellow")
    egg.begin_fill()
    egg.pendown()
    egg.forward(3*w)
    egg.right(90)
    egg.forward(h)

    egg.left(90)
    egg.forward(w)
    egg.right(90)
    egg.forward(h)

    egg.left(90)
    egg.forward(w)
    egg.right(90)
    egg.forward(2*h)

    egg.right(90)
    egg.forward(w)
    egg.left(90)
    egg.forward(h)

    egg.right(90)
    egg.forward(w)
    egg.left(90)
    egg.forward(h)

    egg.right(90)
    egg.forward(3*w)

    egg.right(90)
    egg.forward(h)
    egg.left(90)
    egg.forward(w)

    egg.right(90)
    egg.forward(4*h)

    egg.right(90)
    egg.forward(w)
    egg.left(90)
    egg.forward(h)
    egg.end_fill()
    egg.penup()

    # now add the two 'highlight' pixels...
    draw_pixel(egg, w, h, "black", real_x + w, real_y - h)
    draw_pixel(egg, w, h, "black", real_x, real_y - (2 * h))
    return egg, "egg"


def draw_grain(x: int, y: int) -> (turtle, str):
    """A pile of corn? grain?  Done in the same style as the
    bbc version. """
    real_x = x * tile_width
    real_y = y * tile_height

    grain = turtle.Turtle()
    grain.hideturtle()
    grain.penup()

    # make sure the overlap looks right:
    w = global_w
    h = 2

    # figure out where to start the draw.
    real_x = real_x + (tile_width//2) - (3 * w)
    real_y = real_y - tile_height + h

    grain.setposition(real_x, real_y)
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(2*w), real_y)
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(4*w), real_y)
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(6*w), real_y)
    draw_pixel(grain, w, h, "DarkMagenta")
    # second row
    grain.setposition(real_x+(1*w), real_y + h + 2)
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(3*w), real_y + h + 2)
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(5*w), real_y + h + 2)
    draw_pixel(grain, w, h, "DarkMagenta")
    # third row
    grain.setposition(real_x+(2*w), real_y + (2 * (h + 2)))
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.setposition(real_x+(4*w), real_y + (2 * (h + 2)))
    draw_pixel(grain, w, h, "DarkMagenta")
    # final dot!
    grain.setposition(real_x+(3*w), real_y + (3 * (h + 2)))
    draw_pixel(grain, w, h, "DarkMagenta")
    grain.penup()
    return grain, "grain"


def draw_box(x: int, y: int, colour: str) -> None:
    """ This is used in debug display mode, to show the grid and the
    tile coordinates. """
    real_x = x * tile_width
    real_y = y * tile_height
    box = turtle.Turtle()
    box.hideturtle()
    box.penup()
    box.color(colour)
    box.setheading(90)
    box.pensize(1)
    box.setposition(real_x, real_y)
    box.right(90)
    box.pendown()
    box.forward(tile_width)
    box.right(90)
    box.forward(tile_height)
    box.right(90)
    box.forward(tile_width)
    box.right(90)
    box.forward(tile_height)
    box.penup()
    box.setposition(real_x+5, real_y-tile_height/2)
    box.write(f"({x},{y})", align="left", font=("Consolas", 8, "normal"))
    return


def draw_pixel(thing, w: int, h: int, colour: str, x: int = None, y: int = None):
    """ Function to draw a rectangle """
    if x is not None and y is not None:
        thing.setposition(x, y)
    thing.setheading(0)
    thing.fillcolor(colour)
    thing.begin_fill()
    thing.pencolor(colour)
    thing.pendown()
    thing.forward(w)
    thing.right(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(w)
    thing.right(90)
    thing.forward(h)
    thing.penup()
    thing.end_fill()
    return
