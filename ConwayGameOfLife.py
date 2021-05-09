# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import random
import ulab

from board import SCL, SDA
import busio

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
#print("Default output MIDI channel:", midi.out_channel + 1)

from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2F), NeoTrellis(i2c_bus, False, addr=0x2E)],
    [NeoTrellis(i2c_bus, False, addr=0x32), NeoTrellis(i2c_bus, False, addr=0x30)],
]


# trelli = [
#   [NeoTrellis(i2c_bus, False, addr=0x2e)]
# ]

trellis = MultiTrellis(trelli)
raw_width = 8
raw_height = 8
w_offset = 0
h_offset = 1


def offset_xy(x, y):
    return x + w_offset, y + h_offset


def onset_xy(x, y):
    return x - w_offset, y - h_offset


def offset_x(x):
    return x + w_offset


def offset_y(y):
    return y + h_offset


width = raw_width - w_offset
height = raw_height - h_offset


N = width

# some color definitions
OFF_COLOR = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)


SETUP_BUTTON = (0, 0)
PLAY_BUTTON = (1, 0)
RANDOM_BUTTON = (3, 0)
SPEED_UP_BUTTON = (6, 0)
SPEED_DOWN_BUTTON = (7, 0)

buttons = [SETUP_BUTTON, PLAY_BUTTON, RANDOM_BUTTON, SPEED_UP_BUTTON, SPEED_DOWN_BUTTON]

# NeoTrellis button callback
def button_callback(xcoord, ycoord, edge):
    # turn the LED on when a rising edge is detected
    button = (xcoord, ycoord)
    if edge == NeoTrellis.EDGE_RISING:
        if button == SETUP_BUTTON:
            global game_state
            game_state = GAME_SETUP

        if button == PLAY_BUTTON:
            global game_state
            game_state = GAME_RUNNING

        if button == SPEED_UP_BUTTON:
            global speed
            speed = speed * 2

        if button == SPEED_DOWN_BUTTON:
            global speed
            speed = speed * 0.5

        if button == RANDOM_BUTTON:
            global grid
            grid = randomGrid(height, width)
            print("RANDOM GRID")
            print(grid)

        if button not in buttons:
            #print(button)
            x, y = onset_xy(xcoord, ycoord)
            #print(x, y)
            global grid
            if grid[x, y] == ON:
                grid[x, y] = OFF
                trellis.color(xcoord, ycoord, OFF_COLOR)
            else:
                grid[x, y] = ON
                trellis.color(xcoord, ycoord, PURPLE)

    # turn the LED off when a rising edge is detected
    elif edge == NeoTrellis.EDGE_FALLING:
        if button not in buttons:
            1
            # trellis.color(xcoord, ycoord, OFF)


# Setup NeoTrellis
for y in range(raw_height):
    for x in range(raw_width):
        # activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, button_callback)
        trellis.color(x, y, PURPLE)
        time.sleep(0.005)

for y in range(raw_height):
    for x in range(raw_width):
        trellis.color(x, y, OFF_COLOR)
        time.sleep(0.005)


trellis.color(SETUP_BUTTON[0], SETUP_BUTTON[1], RED)
trellis.color(PLAY_BUTTON[0], PLAY_BUTTON[1], GREEN)
trellis.color(RANDOM_BUTTON[0], RANDOM_BUTTON[1], YELLOW)
trellis.color(SPEED_UP_BUTTON[0], SPEED_UP_BUTTON[1], CYAN)
trellis.color(SPEED_DOWN_BUTTON[0], SPEED_DOWN_BUTTON[1], CYAN)

# CONWAY's Game of Life


def check_game_field():
    for y in range(height):
        y = offset_y(y)
        for x in range(width):
            x = offset_x(x)
            trellis.color(x, y, GREEN)
            time.sleep(0.001)
            trellis.color(x, y, OFF_COLOR)


check_game_field()

OFF = 0
ON = 1

GAME_SETUP = 0
GAME_RUNNING = 1

game_state = GAME_SETUP


def handle_setup():
    1


def update_game(speed):
    # print('Update game')
    time.sleep(speed)


def update_grid(grid, width, height):

    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()
    #print(width)
    #print(height)
    for i in range(width):
        for j in range(height):

            # compute 8-neghbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulaton takes place on a toroidal surface.
            # total = int(grid[i, (j-1)%N] + grid[i, (j+1)%N] +
            #             grid[(i-1)%N, j] + grid[(i+1)%N, j] +
            #             grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
            #             grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N]
            #             )
            #print(grid)
            total = int(
                grid[i, (j - 1) % height]
                + grid[i, (j + 1) % height]
                + grid[(i - 1) % width, j]
                + grid[(i + 1) % width, j]
                + grid[(i - 1) % width, (j - 1) % height]
                + grid[(i - 1) % width, (j + 1) % height]
                + grid[(i + 1) % width, (j - 1) % height]
                + grid[(i + 1) % width, (j + 1) % height]
            )

            # apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON

    # update data
    grid[:] = newGrid[:]
    return grid


def update_LEDs(grid):
    for x in range(width):
        for y in range(height):
            if grid[x, y] == 0:
                trellis.color(x + w_offset, y + h_offset, OFF)
            else:
                trellis.color(x + w_offset, y + h_offset, PURPLE)


def newGrid(width, height):
    grid = ulab.zeros((width, height))
    return grid


def randomGrid(width, height):
    """returns a grid of NxN random values"""
    grid = newGrid(width, height)
    for x in range(width):
        for y in range(height):
            grid[x, y] = random.randint(0, 1)

    return grid


grid = randomGrid(width, height)
grid = newGrid(width, height)
speed = 1

while True:
    # the trellis can only be read every 17 millisecons or so
    trellis.sync()
    time.sleep(0.02)
    # print('game_state={}'.format(game_state))

    if game_state == GAME_SETUP:
        handle_setup()
        #print("Handle setup")
        # grid = randomGrid(width, height)
        # print('New Grid:')
        # print(grid)
        # game_state = GAME_RUNNING

    else:
        update_game(speed)
        grid = update_grid(grid, width, height)
        update_LEDs(grid)

    if game_state != GAME_SETUP:
        cell_sum = ulab.numerical.sum(grid)
        print((cell_sum,))
        if cell_sum == 0:
            #print("Reset game")
            check_game_field()
            game_state = GAME_SETUP
