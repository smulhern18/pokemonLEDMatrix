#!/usr/bin/env python

import random
import time
from PIL import ImageFont, Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from app.databaseHandler import pull_random_pokemon, pull_picture


def pokemonImageResizing(image_name: str) -> Image:
    image = pull_picture(image_name).resize((64, 64))
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
    name_img = Image.new('RGB', (7*len(name), 12), color=(0, 0, 0))

    fnt = ImageFont.truetype('./Anonymous_Pro.ttf', 12)
    d = ImageDraw.Draw(name_img)
    d.text((0, 0), name, font=fnt, fill=(255, 255, 255))

    desc_img = Image.new('RGB', (7*len(desc), 12), color=(0, 0, 0))

    fnt = ImageFont.truetype('./Anonymous_Pro.ttf', 12)
    d = ImageDraw.Draw(desc_img)
    d.text((0, 0), desc, font=fnt, fill=(255, 255, 255))

    return name_img, desc_img


def rgbController():
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 64
    options.chain_length = 2
    options.pixel_mapper_config = 'Rotate:90'
    options.drop_privileges = False
    options.limit_refresh_rate_hz = 120
    options.gpio_mapping = 'adafruit-hat-pwm'

    matrix = RGBMatrix(options=options)

    offscreen_canvas = matrix.CreateFrameCanvas()
    font = graphics.Font()
    font.LoadFont("./Anonymous_Pro.ttf")

    try:
        pos = 0
        cycles = 0
        pokemon = pull_random_pokemon()
        desc = random.sample(pokemon['descriptions'], 1)[0] if pokemon['descriptions'] != [] else ' '*40
        while True:
            offscreen_canvas.Clear()
            secondary_type = None
            name = f"{pokemon['name']}         "
            name = (name * (len(desc)//len(name) + 1)).strip()
            name_img, desc_img = generateTextImages(name, desc)

            name_img = name_img.crop((pos, 0, pos+64, name_img.height))
            desc_img = desc_img.crop((pos, 0, pos+64, desc_img.height))
            pokemon_image = pokemonImageResizing(pokemon['name'] + '.png')
            primary_type = pull_picture(pokemon['primary_type']+'.png')
            secondary_type: Image
            if pokemon['secondary_type']:
                secondary_type = pull_picture(pokemon['secondary_type']+'.png')

            full_image = Image.new('RGB', (64, 128), color=(0, 0, 0))

            full_image.paste(pokemon_image, (0, 0))
            full_image.paste(name_img, (0, 64))
            full_image.paste(desc_img, (0, 108))
            if secondary_type:
                full_image.paste(primary_type, (4, 80))
                full_image.paste(secondary_type, (36, 80))
            else:
                full_image.paste(primary_type, (20, 80))

            offscreen_canvas.SetPixelsPillow(0, 0, 64, 128, full_image)

            synchronizer_len = max(len(name)*7, len(desc)*7)
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            pos += 1

            if synchronizer_len + 1 < pos:
                pos = 0
                cycles += 1
                if cycles > 2:
                    pokemon = pull_random_pokemon()
                    cycles = 0
                    desc = random.sample(pokemon['descriptions'], 1)[0] if pokemon['descriptions'] != [] else '        ' * 2
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
