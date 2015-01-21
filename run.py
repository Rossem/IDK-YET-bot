from image import *

import PIL
from PIL import Image
from PIL import ImageDraw

from quad_constants import * #constants

import heapq
import sys


def run():

    filename = raw_input("enter file: ")

    model = ImageModel(filename)
    previous = None
    
    for i in range(ITERATIONS):
        error = model.average_error()
        if previous is None or previous - error > ERROR_RATE:
            print i, error
            if SAVE_FRAMES:
                model.render('frames/%06d.png' % i)
            previous = error
        model.split()
    model.render('QUAD' + filename)

run()
        


