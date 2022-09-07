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


def pokemonImageResizing(image_name: str) -> Image:
    image = Image.open(io.BytesIO(pull_picture(image_name))).resize((64, 64))
    bounding_box = image.getbbox()
    width = bounding_box[2] - bounding_box[0]
    height = bounding_box[3] - bounding_box[1]
    difference = int(abs(width - height) / 2)
    x0, y0, x1, y1 = bounding_box
    if width > height:
        y1 += (difference + 2)
        y0 -= (difference + 2)
        x1 += 2
        x0 -= 2
    elif width < height:
        x1 += (difference + 2)
        x0 -= (difference + 2)
        y1 += 2
        y0 -= 2
    else:
        x1 += (difference + 2)
        x0 -= (difference + 2)
        y1 += (difference + 2)
        y0 -= (difference + 2)
    image = image.crop((x0, y0, x1, y1))

    return image.resize((64, 64)).convert('RGB')

def generateTextImages(name, desc) -> (Image, Image):
    name_img = Image.new('RGB', (6*len(name), 12), color=(0, 0, 0))

    fnt = ImageFont.truetype('./Anonymous_Pro.ttf', 12)
    d = ImageDraw.Draw(name_img)
    d.text((0, 0), name, font=fnt, fill=(255, 255, 255))

    desc_img = Image.new('RGB', (6*len(desc), 12), color=(0, 0, 0))

    fnt = ImageFont.truetype('./Anonymous_Pro.ttf', 12)
    d = ImageDraw.Draw(desc_img)
    d.text((0, 0), desc, font=fnt, fill=(255, 255, 255))

    return name_img, desc_img


options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 2
options.pixel_mapper_config = 'Rotate:90'
options.drop_privileges = False
options.limit_refresh_rate_hz = 120

matrix = RGBMatrix(options=options)


offscreen_canvas = matrix.CreateFrameCanvas()
font = graphics.Font()
font.LoadFont("./Anonymous_Pro.ttf")
textColor = graphics.Color(255, 255, 255)

try:
    pos = 0
    cycles = 0
    pokemon = pull_random_pokemon()
    while True:
        offscreen_canvas.Clear()
        secondary_type = None
        desc = random.sample(pokemon['descriptions'], 1)[0] if pokemon['descriptions'] != [] else ''
        name = f"{pokemon['name']}         "
        name = (name * (len(desc)//len(name) + 1)).strip()
        name_img, desc_img = generateTextImages(name, desc)

        offscreen_canvas.SetPixelsPillow(0, 0, 64, 64, pokemonImageResizing(pokemon['name'] + '.png'))
        offscreen_canvas.SetPixelsPillow(0, 72, 64, 84, name_img.crop((pos, 0, pos+64, name_img.height)))
        offscreen_canvas.SetPixelsPillow(0, 100, 64, 112, desc_img.crop((pos, 0, pos+64, desc_img.height)))

        synchronizer_len = max(name_img.width, desc_img.width)
        print("before canvas")
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        print("line 97")
        pos -= 1

        if -(synchronizer_len + 1) > pos:
            pos = 0
            cycles += 1
            if cycles > 4:
                pokemon = pull_random_pokemon()
                cycles = 0
        print("line 107")
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
