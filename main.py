#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display a bouncing ball animation and frames per second.
Attribution: https://github.com/rogerdahl/ssd1306/blob/master/examples/bounce.py
"""
import io
import random
import time
from luma.emulator.device import pygame
from PIL import ImageFont, Image, ImageDraw
from luma.core.render import canvas
from luma.core.image_composition import ImageComposition, ComposableImage

from databaseHandler import pull_random_pokemon, pull_picture


class TextImage:
    def __init__(self, idevice, text, font):
        with canvas(idevice) as idraw:
            _, _, w, h = idraw.textbbox(xy=(0, 0), text=text, font=font)
        self.image = Image.new(idevice.mode, (w, h))
        idraw = ImageDraw.Draw(self.image)
        idraw.text((0, 0), text, fill="white", font=font)
        del idraw
        self.width = w
        self.height = h

    def crop(self, box):
        return self.image.crop(box)

class Synchroniser():
    def __init__(self):
        self.synchronised = {}

    def busy(self, task):
        self.synchronised[id(task)] = False

    def ready(self, task):
        self.synchronised[id(task)] = True

    def is_synchronised(self):
        for task in self.synchronised.items():
            if task[1] is False:
                return False
        return True


class Scroller:
    WAIT_SCROLL = 1
    SCROLLING = 2
    WAIT_REWIND = 3
    WAIT_SYNC = 4

    def __init__(self, s_image_composition, rendered_image, scroll_delay, synch, speed: float = 0.66):
        self.image_composition = s_image_composition
        self.speed = speed
        self.image_x_pos = 0
        self.rendered_image = rendered_image
        self.image_composition.add_image(rendered_image)
        self.max_pos = rendered_image.width - s_image_composition().width
        self.delay = scroll_delay
        self.ticks = 0
        self.state = self.WAIT_SCROLL
        self.synchroniser = synch
        self.render()
        self.synchroniser.busy(self)
        self.cycles = 0
        self.must_scroll = self.max_pos > 0

    def __del__(self):
        self.image_composition.remove_image(self.rendered_image)

    def tick(self):

        # Repeats the following sequence:
        #  wait - scroll - wait - rewind -> sync with other scrollers -> wait
        if self.state == self.WAIT_SCROLL:
            if not self.is_waiting():
                self.cycles += 1
                self.state = self.SCROLLING
                self.synchroniser.busy(self)

        elif self.state == self.WAIT_REWIND:
            if not self.is_waiting():
                self.synchroniser.ready(self)
                self.state = self.WAIT_SYNC

        elif self.state == self.WAIT_SYNC:
            if self.synchroniser.is_synchronised():
                if self.must_scroll:
                    self.image_x_pos = 0
                    self.render()
                self.state = self.WAIT_SCROLL

        elif self.state == self.SCROLLING:
            if self.image_x_pos < self.max_pos:
                if self.must_scroll:
                    self.render()
                    self.image_x_pos += self.speed
            else:
                self.state = self.WAIT_REWIND

    def render(self):
        self.rendered_image.offset = (self.image_x_pos, 0)

    def is_waiting(self):
        self.ticks += 1
        if self.ticks > self.delay:
            self.ticks = 0
            return False
        return True

    def get_cycles(self):
        return self.cycles


def make_font():
    font_path = './Anonymous_Pro.ttf'
    return ImageFont.truetype(font_path, 12)


device = pygame(width=64, height=128)

image_composition = ImageComposition(device)


try:
    while True:
        secondary_type = None
        pokemon = pull_random_pokemon()
        synchroniser = Synchroniser()
        desc = random.sample(pokemon['descriptions'], 1)[0] if pokemon['descriptions'] != [] else ''
        name = f"{pokemon['name']}         "
        name = (name * (len(desc)//len(name) + 1)).strip()
        poke_name = ComposableImage(TextImage(device, name, make_font()).image, position=(2, 64))
        poke_image = ComposableImage(Image.open(io.BytesIO(pull_picture(pokemon['name']+'.png'))).resize((64, 64)), position=(0, 0))
        poke_description = ComposableImage(TextImage(device, desc, make_font()), position=(2, 108))
        if pokemon['secondary_type']:
            primary = ComposableImage(Image.open(io.BytesIO(pull_picture(pokemon['primary_type']+'.png'))), position=(4, 80))
            secondary = ComposableImage(Image.open(io.BytesIO(pull_picture(pokemon['secondary_type']+'.png'))), position=(36, 80))
            secondary_type = Scroller(image_composition, secondary, 50, synchroniser)
        else:
            primary = ComposableImage(Image.open(io.BytesIO(pull_picture(pokemon['primary_type']+'.png'))), position=(20, 80))
        primary_type = Scroller(image_composition, primary, 50, synchroniser)
        name = Scroller(image_composition, poke_name, 50, synchroniser)
        image = Scroller(image_composition, poke_image, 50, synchroniser)
        description = Scroller(image_composition, poke_description, 50, synchroniser, speed=0.66)

        cycles = 0

        while cycles < 5:
            name.tick()
            image.tick()
            primary_type.tick()
            description.tick()
            if secondary_type:
                secondary_type.tick()
            time.sleep(0.025)
            cycles = name.get_cycles()

            with canvas(device, background=image_composition()) as draw:
                image_composition.refresh()

        del name

except KeyboardInterrupt:
    pass
