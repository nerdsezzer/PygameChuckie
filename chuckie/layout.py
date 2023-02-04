import turtle

from config import tile_width, tile_height


def _draw_thing_outline(thing, start_x, start_y, width, height, colour):
    """
    Function for use during debug, which shows outline of the
    moving 'thing'.
    """
    thing.setposition(start_x + (tile_width / 2), start_y - (tile_height / 2))
    thing.dot(10, "red")

    thing.setposition(start_x, start_y)
    thing.pensize(5)
    thing.pencolor(colour)
    thing.pendown()
    thing.setheading(0)
    thing.forward(width)
    thing.right(90)
    thing.forward(height)
    thing.right(90)
    thing.forward(width)
    thing.right(90)
    thing.forward(height)
    thing.penup()

    thing.setposition(start_x, start_y)
    thing.dot(10, "cyan")
    return
