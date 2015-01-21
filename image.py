import PIL
from PIL import Image
from PIL import ImageDraw

import ImageMagick

from quad_constants import * #constants

import heapq
import sys


#---------------------------------------------
#Helper functions

def avg(histogram):
    
    total = sum(histogram)
    value = 0

    for i, x in enumerate(histogram):
        value += i * x

    value /= total
    error = error ** 0.5
    
    return value, error

def get_color_histogram(histogram):
    r, r1 = avg(histogram[:256])
    g, g1 = avg(histogram[256:512])
    b, b1 = avg(histogram[512:768])
    
    e1 = r1 * 0.2989 + g1 * 0.5870 + b1 * 0.1140

    return (r,g,b), e1



#---------------------------------------------
#Classes

class Quad(object):
    
    def __init__(self, model, box, depth):
        self.model = model
        self.box = box
        self.depth = depth

class ImageModel(object):

    def __init__(self):
        pass




