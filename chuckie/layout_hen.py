import turtle

import config
from config import tile_width, tile_height, global_w, global_h
from chuckie.layout_elements import draw_pixel
from chuckie.layout import _draw_thing_outline
from chuckie.layout_harry import _draw_head, _draw_body


def _draw_hen_head(hen, x, y, w, h, step, left_func, right_func):
    hen.setposition(x, y)
    if hen.direction == 'left':
        hen.setheading(180)
    else:
        hen.setheading(0)
    hen.fillcolor("cyan")
    hen.begin_fill()
    hen.pendown()

    hen.forward(2 * w)
    right_func(90)
    hen.forward(h)
    left_func(90)

    if step == 2 or step == 4:
        hen.forward(2 * w)
        right_func(90)
        hen.forward(h)
        right_func(90)
        hen.forward(2 * w)
    else:
        hen.forward(2 * w)
        left_func(90)
        hen.forward(h)
        left_func(90)
        hen.forward(w)
        left_func(90)
        hen.forward(3 * h)
        left_func(90)
        hen.forward(w)
        left_func(90)
        hen.forward(h)
        left_func(90)
        hen.forward(2 * w)

    left_func(90)
    hen.forward(h)
    right_func(90)
    hen.forward(w)
    left_func(90)
    hen.forward(2 * h)
    right_func(90)
    hen.forward(w)
    right_func(90)
    hen.forward(2 * h)
    left_func(90)
    hen.forward(w)
    right_func(90)
    hen.forward(2 * h)
    right_func(90)
    hen.forward(w)
    left_func(90)
    hen.forward(h)
    hen.penup()
    hen.end_fill()
    return


def _draw_hen_body(hen, x, y, w, h, state, left_func, right_func):
    if state == 'left':
        hen.setheading(180)
    else:
        hen.setheading(0)

    hen.setposition(x, y)
    hen.pencolor("cyan")
    hen.fillcolor("cyan")
    hen.begin_fill()
    hen.pendown()

    hen.forward(w)
    right_func(90)
    hen.forward(2 * h)
    left_func(90)

    hen.forward(w)
    right_func(90)
    hen.forward(3 * h)
    right_func(90)

    hen.forward(w)
    left_func(90)
    hen.forward(h)
    right_func(90)

    hen.forward(2 * w)
    left_func(90)
    hen.forward(h)
    right_func(90)

    hen.forward(2 * w)
    right_func(90)
    hen.forward(h)
    left_func(90)

    hen.forward(w)
    right_func(90)
    hen.forward(h)
    left_func(90)

    hen.forward(w)
    right_func(90)
    hen.forward(3 * h)
    right_func(90)

    hen.forward(w)
    left_func(90)
    hen.forward(h)
    right_func(90)

    hen.forward(2 * w)
    right_func(90)
    hen.forward(h)
    left_func(90)

    hen.forward(w)
    right_func(90)
    hen.forward(h)
    left_func(90)

    hen.forward(w)
    left_func(90)
    hen.forward(3 * h)
    hen.penup()
    hen.end_fill()
    return


def _draw_legs(hen, real_x, real_y, w, h, step, state):
    if state == "up-down":
        _draw_up_down_legs(hen, real_x - w, real_y - (16 * h), w, h, 5, "cyan", step)
    elif state == 'right' or state == 'eating-right':
        if step == 1 or step == 3:
            # front leg
            hen.setposition(real_x, real_y - (14 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x + w, real_y - (16 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x + (2 * w), real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
            hen.setposition(real_x + (3 * w), real_y - (17 * h))
            draw_pixel(hen, w, h, "cyan")

            # back leg
            hen.setposition(real_x - (2 * w), real_y - (14 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x - (3 * w), real_y - (16 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x - (2 * w), real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
        else:
            hen.setposition(real_x, real_y - (14 * h))
            draw_pixel(hen, w, h * 5, "cyan")
            hen.setposition(real_x + w, real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
    else:
        if step == 1 or step == 3:
            hen.setposition(real_x - w, real_y - (14 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x - (2 * w), real_y - (16 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x - (3 * w), real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
            hen.setposition(real_x - (4 * w), real_y - (17 * h))
            draw_pixel(hen, w, h, "cyan")

            # back leg
            hen.setposition(real_x + w, real_y - (14 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x + (2 * w), real_y - (16 * h))
            draw_pixel(hen, w, h * 2, "cyan")
            hen.setposition(real_x + w, real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
        else:
            hen.setposition(real_x - w, real_y - (14 * h))
            draw_pixel(hen, w, h * 5, "cyan")
            hen.setposition(real_x - (2 * w), real_y - (18 * h))
            draw_pixel(hen, w, h, "cyan")
    return


def _draw_up_down_legs(thing, x, y, w, h, length, colour, step):
    thing.setheading(0)

    y = y + h
    left_leg = x - w
    right_leg = x + (2 * w)

    if step == 1:
        # left leg extended (4 high), right leg sideways only.
        # left leg
        thing.setposition(left_leg, y + h)
        draw_pixel(thing, w, ((length + 1) * h), colour)
        thing.setposition(left_leg - w, y + h - ((length+1) * h))
        draw_pixel(thing, w, h, colour)

        # right leg
        thing.setposition(right_leg, y + h)
        draw_pixel(thing, (2 * w), h, colour)

    elif step == 2 or step == 4:
        # left leg
        thing.setposition(left_leg, y + h)
        draw_pixel(thing, w, (5 * h), colour)
        thing.setposition(left_leg - w, y + h - (4 * h))
        draw_pixel(thing, w, h, colour)
        # right leg
        thing.setposition(right_leg, y + h)
        draw_pixel(thing, w, (5 * h), colour)
        thing.setposition(right_leg + w, y + h - (4 * h))
        draw_pixel(thing, w, h, colour)

    else:  # step == 3
        # left sideways only, leg extended (4 high).
        # left leg
        thing.setposition(left_leg - w, y + h)
        draw_pixel(thing, (2 * w), h, colour)
        # right leg
        thing.setposition(right_leg, y + h)
        draw_pixel(thing, w, ((length + 1) * h), colour)
        thing.setposition(right_leg + w, y + h - ((length+1) * h))
        draw_pixel(thing, w, h, colour)
    return


def _draw_body_eating(thing, x, y, w, h, colour, step, state, left, right):
    if state == 'eating-left':
        thing.setheading(180)
        x = x + w if step == 2 else x + (2 * w)
    else:
        thing.setheading(0)
        x = x - w

    original_left = thing.left
    thing.left = left
    original_right = thing.right
    thing.right = right

    thing.setposition(x, y)
    thing.pencolor(colour)
    thing.pendown()
    thing.fillcolor(colour)
    thing.begin_fill()

    # from his butt to his neck
    thing.forward(2 * w)
    thing.left(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(w)
    thing.left(90)
    if step == 2:
        thing.forward(h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(w)
    thing.left(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(2 * w)

    # now do the neck and the head.
    if step == 2:
        thing.forward(4*w)
        thing.left(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(2*h)
        thing.left(90)
        thing.forward(w)
        thing.right(90)
        thing.forward(3*h)
        thing.left(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(3*h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(3*w)
        thing.right(90)
        thing.forward(2*h)
    else:
        thing.right(90)
        thing.forward(h)
        thing.left(90)
        thing.forward(w)
        thing.right(90)
        thing.forward(h)
        thing.left(90)
        thing.forward(w)
        thing.right(90)
        thing.forward(2*h)
        thing.left(90)
        thing.forward(3*w)      # across the top of it's head.
        thing.left(90)
        thing.forward(3*h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(h)
        thing.left(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(w)
        thing.left(90)
        thing.forward(h)
        thing.right(90)
        thing.forward(3*w)      # underneath of the head.
        thing.right(90)
        thing.forward(2*h)
        thing.left(90)
        thing.forward(w)
        thing.right(90)
        thing.forward(h)
        thing.left(90)
        thing.forward(w)
        thing.right(90)
        thing.forward(3*h)

    thing.left(90)
    thing.forward(w)
    thing.right(90)
    thing.forward(h)
    thing.left(90)
    thing.forward(2*w)
    thing.left(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(w)  # this should over lap with his leg now.
    thing.forward(w)
    thing.left(90)
    thing.forward(h)
    thing.right(90)
    thing.forward(w)
    thing.left(90)
    thing.forward(2*h)
    thing.right(90)
    thing.forward(w)
    thing.left(90)
    thing.forward(4*h)
    thing.left(90)
    thing.forward(w)
    thing.right(90)
    thing.forward(h)
    thing.end_fill()
    thing.penup()

    thing.left = original_left
    thing.right = original_right

    if state == 'eating-left':
        if step == 1 or step == 3:
            draw_pixel(thing, w, h, "black", x - (10 * w), y)
        else:
            draw_pixel(thing, w, (2*h), "black", x - (11 * w), y - (5*h))
    else:
        if step == 1 or step == 3:
            draw_pixel(thing, w, h, "black", x + (9 * w), y)
        else:
            draw_pixel(thing, w, (2*h), "black", x + (10 * w), y - (5*h))

    return


def draw_hen(hen):
    """
    Hens are more different depending on left/right, compared to Harry
    So this class messes with the left() and right() functions to draw
    mirror images of the 'parts'.
    """
    real_x = hen.hx
    real_y = hen.hy

    state = "up-down" if hen.hy_velocity != 0 else ("left" if hen.hx_velocity < 0 else "right")
    if hen.direction == 'eating':
        state = 'eating-'+hen.previous_direction

    hen.animation_step += 1
    if hen.direction == 'eating' and hen.animation_step == 4:
        hen.direction = state[len('eating-'):]
        state = hen.direction
        hen.hx_velocity = config.hen_default_hx_velocity if hen.direction == 'right' else 0-config.hen_default_hy_velocity

    if hen.animation_step == 5:
        hen.animation_step = 1
    step = hen.animation_step

    #print(f"state = {state}, {hen.animation_step}")

    hen.clear()

    if config.debug_display:
        _draw_thing_outline(hen, hen.hx, hen.hy, tile_width, tile_height*2, "green")
    else:
        pen_size = 1
        w = global_w
        h = global_h

        real_x += tile_width // 2
        real_y -= (3*h) - 1
        hen.setposition(real_x, real_y)
        hen.pensize(pen_size)
        hen.pencolor("cyan")
        hen.fillcolor("cyan")
        hen.setheading(0)

        # draw the head.
        if state == 'left':
            _draw_hen_head(hen, real_x, real_y, w, h, step, hen.right, hen.left)
            draw_pixel(hen, w, h, "black", real_x - (2 * w), real_y - h)            # draw the eye
            draw_pixel(hen, w, 2 * h, "cyan", real_x - (2 * w), real_y - (5 * h))  # draw the neck
            _draw_hen_body(hen, real_x - (2 * w), real_y - (7 * h), w, h, state, hen.right, hen.left)
            _draw_legs(hen, real_x, real_y, w, h, step, state)

        elif state == 'eating-left':
            _draw_body_eating(hen, real_x, real_y - (6 * h), w, h, "cyan", step, state, hen.left, hen.right)
            _draw_legs(hen, real_x, real_y, w, h, 2, state)

        elif state == 'right':
            _draw_hen_head(hen, real_x, real_y, w, h, step, hen.left, hen.right)
            draw_pixel(hen, w, h, "black", real_x + w, real_y - h)                  # draw the eye
            draw_pixel(hen, w, 2 * h, "cyan", real_x + w, real_y - (5 * h))        # draw the neck
            _draw_hen_body(hen, real_x + (2 * w), real_y - (7 * h), w, h, state, hen.left, hen.right)
            _draw_legs(hen, real_x, real_y, w, h, step, state)

        elif state == 'eating-right':
            _draw_body_eating(hen, real_x, real_y - (6 * h), w, h, "cyan", step, state, hen.right, hen.left)
            _draw_legs(hen, real_x, real_y, w, h, 2, state)

        elif state == 'up-down':
            _draw_head(hen, real_x - w, real_y, w, h, "cyan", state, no_brim=True)
            draw_pixel(hen, 2 * w, 3 * h, "cyan", real_x - w, real_y - (4 * h))
            _draw_body(hen, real_x - w, real_y - (7 * h), w, h, "cyan")
            _draw_legs(hen, real_x, real_y, w, h, step, state)

    return



