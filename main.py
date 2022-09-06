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
from PIL import ImageFont, Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from databaseHandler import pull_random_pokemon, pull_picture


options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 2
options.pixel_mapper_config = 'Rotate:90'
options.drop_privileges = False

matrix = RGBMatrix(options = options)


offscreen_canvas = matrix.CreateFrameCanvas()
font = graphics.Font()
font.LoadFont("./Anonymous_Pro.ttf")
textColor = graphics.Color(255, 255, 255)

try:
    pos = offscreen_canvas.width
    cycles = 0
    pokemon = pull_random_pokemon()
    while True:
        offscreen_canvas.Clear()
        secondary_type = None
        desc = random.sample(pokemon['descriptions'], 1)[0] if pokemon['descriptions'] != [] else ''
        desc_len = graphics.DrawText(offscreen_canvas, font, pos, 66, textColor, desc)
        name = f"{pokemon['name']}         "
        name = (name * (len(desc)//len(name) + 1)).strip()
        name_len = graphics.DrawText(offscreen_canvas, font, pos, 120, textColor, name)
        synchronizer_len = max(name_len, desc_len)

        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        pos -= 1

        if pos + synchronizer_len + 1 < 0:
            pos = offscreen_canvas.width
            cycles += 1
            if cycles > 4:
                pokemon = pull_random_pokemon()
                cycles = 0

        time.sleep(0.05)

except KeyboardInterrupt:
    pass
