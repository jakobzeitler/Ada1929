# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import random

from board import SCL, SDA
import busio

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.pitch_bend import PitchBend

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
print("Default output MIDI channel:", midi.out_channel + 1)

from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# create the i2c object for the trellis
i2c_bus = busio.I2C(SCL, SDA)

trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2F), NeoTrellis(i2c_bus, False, addr=0x2E)],
    [NeoTrellis(i2c_bus, False, addr=0x32), NeoTrellis(i2c_bus, False, addr=0x30)],
]


#trelli = [
#   [NeoTrellis(i2c_bus, False, addr=0x2e)]
#]

trellis = MultiTrellis(trelli, rotation=90)

# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

BASE_NOTE = 44
# NeoTrellis button callback
def button_callback(xcoord, ycoord, edge):
    # turn the LED on when a rising edge is detected
    note_level = 44 + xcoord + ycoord * 8
    print(note_level)
    if edge == NeoTrellis.EDGE_RISING:
        for i in range(8):
            trellis.color(xcoord, i, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) )
            trellis.color(i, ycoord, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) )
        midi.send(NoteOn(note_level, 120))
    # turn the LED off when a rising edge is detected
    elif edge == NeoTrellis.EDGE_FALLING:
        trellis.color(xcoord, ycoord, OFF)
        for i in range(8):
            trellis.color(xcoord, i, OFF)
            trellis.color(i, ycoord, OFF)
        midi.send(NoteOff(note_level, 120))


# Setup NeoTrellis
for y in range(trellis.pixels.height):
    for x in range(trellis.pixels.width):
        # activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, button_callback)
        trellis.color(x, y, PURPLE)
        time.sleep(0.01)

for y in range(trellis.pixels.height):
    for x in range(trellis.pixels.width):
        trellis.color(x, y, OFF)
        time.sleep(0.02)

while True:
    # the trellis can only be read every 17 millisecons or so
    trellis.sync()
    time.sleep(0.02)
    print('update')

    #for y in range(8):
    #    for x in range(8):
    #        trellis.color(x, y, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) )

    #msg = midi.receive()
    #if msg is not None:
    #    print("Received:", msg, "at", time.monotonic())

