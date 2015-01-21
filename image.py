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

def rnd_rectangle(draw, box, radius, color):
    l,t,r,b = box
    d = radius * 2

    draw.ellipse((l, t, l + d, t + d), color)
    draw.ellipse((r - d, t, r, t + d), color)
    draw.ellipse((l, b - d, l + d, b), color)
    draw.ellipse((r - d, b - d, r, b), color)

    d = radius

    draw.rectangle((l, t + d, r, b - d), color)
    draw.rectangle((l + d, t, r - d, b), color)

#---------------------------------------------
#Classes

class Quad(object):
    
    def __init__(self, model, box, depth):
        self.model = model
        self.box = box
        self.depth = depth

        hist = self.model.im.crop(self.box).histogram()
        self.color, self.error = get_color_histogram(hist)
        self.leaf = self.is_leaf()
        self.area = self.get_area()

        self.children = []

    def is_leaf(self):
        l,t,r,b = self.box
        return int(r-l <= LEAF_SIZE or b-t <= LEAF_SIZE)

    def get_area(self):
        l,t,r,b = self.box
        return (r-l) * (b-t)

    def split(self):
        l,t,r,b = self.box
        lr = l + (r-l)/2
        tb = t + (b-t)/2

        depth = self.depth + 1

        tl = Quad(self.model, (l,t,lr,tb), depth)
        tr = Quad(self.model, (lr,t,r,tb), depth)
        bl = Quad(self.model, (l,tb,lr,b), depth)
        br = Quad(self.modelm (lr,tb,r,b), depth)

        self.children = (tl,tr,bl,br)
        
        return self.children

    def get_leaf_nodes(self, max_depth=None):
        if not self.children:
            return [self]
        if max_depth is not Nine and self.depth >= max_depth:
            return [self]
        result = []
        
        for child in self.children:
            result.extend(child.get_leaf_nodes(max_depth))

        return result


class ImageModel(object):

    def __init__(self):
        pass




