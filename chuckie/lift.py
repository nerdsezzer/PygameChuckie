#import turtle
import pygame
import os

import config
from config import global_w, global_h
from chuckie.thing import Thing
import chuckie.utils as utils


class Lift(Thing):

    def __init__(self, level, start_tile_x, start_tile_y, direction):
        super().__init__('lift', level)

        file = "lift-left.png" if direction == "left" else "lift-right.png"
        self.image = pygame.image.load(os.path.join('.', 'images', file)).convert()
        #img.convert_alpha()
        #img.set_colorkey(ALPHA)
        print(f"putting a lift at [{start_tile_x}, {start_tile_y}]")
        self.rect = self.image.get_rect()
        self.rect.x = start_tile_x * config.tile_width
        self.rect.y = start_tile_y * config.tile_height

        self.state = False
        self.direction = direction
        self.previous_direction = "still"
        (self.hx, self.hy) = utils.tile_to_real(start_tile_x, start_tile_y)
        self.draw()
        return

    @property
    def hy(self):
        return self._hy

    @hy.setter
    def hy(self, value):
        self._hy = value
        self.rect.y = value
        return

    def move(self):
        """
        move the lifts, upwards.  If they reach the top, they respawn at the
        bottom of the screen.
        """
        self.hy += config.lift_default_hy_velocity
        if self.hy >= config.window_height:  # config.top_limit_for_lift:
            self.hy = config.bottom_limit

        if config.debug_lifts:
            self.dump_state("lift: ")
        self.draw()
        return

    def draw(self): # -> (turtle, str):
        return

        """
        lift = self
        lift.clear()

        if config.debug_lifts or config.debug_lifts:
            lift.setposition(lift.hx, lift.hy)
            lift.dot(10, "red")
            lift.pensize(5)
            lift.pencolor("NavyBlue")
            lift.pendown()
            lift.setheading(0)
            lift.forward(config.tile_width)
            lift.right(90)
            lift.forward(config.tile_height)
            lift.right(90)
            lift.forward(config.tile_width)
            lift.right(90)
            lift.forward(config.tile_height)
            lift.penup()
            return

        x = lift.hx
        y = lift.hy - 4
        w = global_w  # was 5
        h = global_h  # was 3
        lift_width = 6*w

        x = (x + config.tile_width - lift_width) if lift.direction == 'left' else x
        lift.setposition(x, y)
        lift.setheading(0)
        lift.pensize(1)
        lift.color("yellow")
        lift.fillcolor("yellow")
        lift.begin_fill()
        lift.pendown()
        lift.forward(lift_width)
        lift.right(90)
        lift.forward(4*h)
        lift.right(90)
        lift.forward(w)
        lift.right(90)
        lift.forward(h)
        lift.left(90)
        lift.forward(w)
        lift.right(90)
        lift.forward(h)
        lift.left(90)
        lift.forward(2*w)
        lift.left(90)
        lift.forward(h)
        lift.right(90)
        lift.forward(w)
        lift.left(90)
        lift.forward(h)
        lift.right(90)
        lift.forward(w)
        lift.right(90)
        lift.forward(4*h)
        lift.penup()
        lift.end_fill()
        return"""
