import turtle

import config
from config import tile_width, tile_height, global_w, global_h
from chuckie.layout_elements import draw_pixel
from chuckie.layout import _draw_thing_outline


def _draw_head(thing, x, y, w, h, colour, state, no_brim=False):
    """
    x and y need to be the topmost left corner the hat.
    This function is also called to draw the birds head, when they're
    climbing the ladder.
    """

    #                |
    #                <><>
    #              <>    <>
    #        ******<>    <>******
    #              <>    <>
    #              <><><><>
    #
    thing.setposition(x, y)
    thing.setheading(0)
    thing.pendown()
    thing.fillcolor(colour)
    thing.begin_fill()
    thing.pencolor(colour)
    thing.forward(w * 2)
    thing.right(90)
    thing.forward(h)
    thing.left(90)
    thing.forward(w)
    thing.right(90)
    thing.forward(h)

    if not no_brim:
        thing.left(90)
        thing.forward(w * 2)  # hat brim ...
        thing.right(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(w * 2)  # ... and back again.
        thing.left(90)

    thing.forward(2 * h)
    thing.right(90)
    thing.forward(4 * w)  # bottom of head.
    thing.right(90)
    thing.forward(2 * h)

    if not no_brim:
        thing.left(90)
        thing.forward(2 * w)  # forward brim...
        thing.right(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(2 * w)  # ... and back again.
        thing.left(90)

    thing.forward(h)
    thing.right(90)
    thing.forward(w)
    thing.left(90)
    thing.forward(h)
    thing.end_fill()
    thing.penup()
    return


def _draw_eyes(thing, x, y, w, h, state):
    if thing.name == 'harry':
        eye_x = x
        eye_y = y - (3 * h)     # eyes are two 'rows' down from top of hat.
        if state == "left":
            draw_pixel(thing, w, h, "black", eye_x, eye_y)
        elif state == "right":
            draw_pixel(thing, w, h, "black", eye_x + w, eye_y)
    return


def _draw_neck(thing, x, y, w, h, state):
    # draw the neck, a single pixel at "back" of the next, depending on
    # direction, or both for when going up/down.
    if state == 'left':
        draw_pixel(thing, w, h, "yellow", x + w, y)
    elif state == 'right':
        draw_pixel(thing, w, h, "yellow", x, y)
    else:
        draw_pixel(thing, (2 * w), h, "yellow", x, y)
    return


def _draw_body(harry, x, y, w, h, colour):
    """
    Starts drawing from the first 'down' at the front of the body (when going left).
    """
    # do the body
    harry.setposition(x, y)
    harry.setheading(0)
    harry.pencolor(colour)
    harry.pendown()
    harry.fillcolor(colour)
    harry.begin_fill()

    harry.forward(2*w)
    harry.right(90)
    harry.forward(h)
    harry.left(90)
    harry.forward(w)

    harry.right(90)
    harry.forward(h)
    harry.left(90)
    harry.forward(w)

    back_x, back_y = harry.pos()
    harry.right(90)
    harry.forward(h * 4)  # his back

    harry.right(90)
    harry.forward(w)
    harry.left(90)
    harry.forward(h)

    harry.right(90)
    harry.forward(w)
    harry.left(90)
    harry.forward(h)

    butt_x, butt_y = harry.pos()

    harry.right(90)
    harry.forward(2 * w)
    harry.right(90)
    harry.forward(h)

    harry.left(90)
    harry.forward(w)
    harry.right(90)
    harry.forward(h)

    harry.left(90)
    harry.forward(w)
    harry.right(90)
    harry.forward(h * 4)

    harry.right(90)
    harry.forward(w)
    harry.left(90)
    harry.forward(h)

    harry.right(90)
    harry.forward(w)
    harry.left(90)
    harry.forward(h)

    harry.right(90)
    harry.end_fill()
    harry.penup()
    return back_x, back_y, butt_x, butt_y


def _draw_arms(harry, x, y, w, h, colour, state, step):
    arm_x = x            # default to arm position for 'left'
    arm_y = y - (2 * h)

    # top of arm.
    if state == "left":
        draw_pixel(harry, w, h * 2, "black", arm_x + w, arm_y)
    elif state == "right":
        draw_pixel(harry, w, h * 2, "black", arm_x, arm_y)

    # bottom of the arm.
    arm_y -= 2 * h
    if state == "left":
        arm_x += w
        if step == 1:
            draw_pixel(harry, w, h * 2, "black", arm_x - w, arm_y)
        elif step == 2 or step == 4:
            draw_pixel(harry, w, h * 2, "black", arm_x, arm_y)
        else:
            draw_pixel(harry, w, h * 2, "black", arm_x + w, arm_y)
    elif state == "right":
        if step == 1:
            draw_pixel(harry, w, h * 2, "black", arm_x - w, arm_y)
        elif step == 2 or step == 4:
            draw_pixel(harry, w, h * 2, "black", arm_x, arm_y)
        else:
            draw_pixel(harry, w, h * 2, "black", arm_x + w, arm_y)
    else:
        left_arm = x - (3 * w)
        right_arm = x + (4 * w)
        arm_y += 2 * h
        if step == 1:
            draw_pixel(harry, w, h * 4, colour, left_arm, arm_y)
            draw_pixel(harry, w, h * 4, colour, right_arm, arm_y + (4 * h))
        elif step == 2 or step == 4:
            draw_pixel(harry, w, h * 2, colour, left_arm, arm_y)
            draw_pixel(harry, w, h * 2, colour, right_arm, arm_y)
        else:
            draw_pixel(harry, w, h * 4, colour, left_arm, arm_y + (4 * h))
            draw_pixel(harry, w, h * 4, colour, right_arm, arm_y)
    return


def _draw_legs(harry, x, y, w, h, colour, state, step):
    left_leg_x = x + (2*w)
    right_leg_x = x
    leg_y = y

    if state == "left":
        if step == 1 or step == 3:
            draw_pixel(harry, w, h, colour, left_leg_x, leg_y + h)
            draw_pixel(harry, w, h, colour, left_leg_x + w, leg_y)
            draw_pixel(harry, w, h, colour, left_leg_x, leg_y - h)

            draw_pixel(harry, w, h, colour, right_leg_x, leg_y)
            draw_pixel(harry, w, h, colour, right_leg_x - w, leg_y - h)
            draw_pixel(harry, w, h, colour, right_leg_x - (2 * w), leg_y)

        elif step == 2 or step == 4:
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y)
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y - h)
            draw_pixel(harry, w, h, colour, left_leg_x - (2 * w), leg_y - h)

    elif state == "right":
        if step == 1 or step == 3:
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y)
            draw_pixel(harry, w, h, colour, left_leg_x, leg_y - h)
            draw_pixel(harry, w, h, colour, left_leg_x + w, leg_y)

            draw_pixel(harry, w, h, colour, right_leg_x - w, leg_y + h)
            draw_pixel(harry, w, h, colour, right_leg_x - (2 * w), leg_y)
            draw_pixel(harry, w, h, colour, right_leg_x - w, leg_y - h)

        elif step == 2 or step == 4:
            draw_pixel(harry, w, h, colour, left_leg_x - (2 * w), leg_y)
            draw_pixel(harry, w, h, colour, left_leg_x - (2 * w), leg_y - h)
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y - h)

    else:
        left_leg_x = x - (1 * w)
        right_leg_x = x + w
        leg_y += h
        if step == 1:
            draw_pixel(harry, w, (4 * h), colour, left_leg_x, leg_y)
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y - (3 * h))
            draw_pixel(harry, (2 * w), h, colour, right_leg_x, leg_y)

        elif step == 2 or step == 4:
            draw_pixel(harry, w, (3 * h), colour, left_leg_x, leg_y + h)
            draw_pixel(harry, w, h, colour, left_leg_x - w, leg_y - h)
            draw_pixel(harry, w, (3 * h), colour, right_leg_x, leg_y + h)
            draw_pixel(harry, w, h, colour, right_leg_x + w, leg_y - h)

        else:  # step == 3
            draw_pixel(harry, (2 * w), h, colour, left_leg_x - w, leg_y)
            draw_pixel(harry, w, (4 * h), colour, right_leg_x, leg_y)
            draw_pixel(harry, w, h, colour, right_leg_x + w, leg_y - (3 * h))
    return


def draw_harry(harry):
    """
    draw harry: head, hat and eye, body, arms and legs.
    He can either be going left or right or up/down.
    """
    real_x = harry.hx
    real_y = harry.hy

    state = "up-down" if harry.hy_velocity != 0 and harry.direction != 'jump' and harry.direction != 'falling' \
        else ("left" if harry.hx_velocity < 0 else "right")
    if harry.on_lift:
        state = harry.direction

    if harry.on_lift:
        harry.animation_step = 2
    else:
        harry.animation_step += 1
        if harry.animation_step == 5:
            harry.animation_step = 1

    step = harry.animation_step

    # first clear out existing Harry
    harry.clear()

    if config.debug_display:
        _draw_thing_outline(harry, real_x, real_y, tile_width, tile_height*2, "purple")
    else:
        pen_size = 1
        w = global_w
        h = global_h

        harry.pensize(pen_size)
        harry.color("yellow")
        harry.setheading(0)

        x = real_x + (tile_width // 2) - w
        y = real_y - (tile_height * 2) + (16 * h)
        _draw_head(harry, x, y, w, h, "yellow", state)
        _draw_eyes(harry, x, y, w, h, state)
        _draw_neck(harry, x, y - (5 * h), w, h, state)
        _draw_body(harry, x, y - (6 * h), w, h, "yellow")
        _draw_arms(harry, x, y - (6 * h), w, h, "yellow", state, step)
        _draw_legs(harry, x, y - (14 * h), w, h, "yellow", state, step)

    return

