import PIL
from PIL import Image
from PIL import ImageDraw

from quad_constants import * #constants

import heapq
import sys


#---------------------------------------------
#Helper functions for histograms

def avg(histogram):
    """this functions get the weighted average of a histogram"""

    total = sum(histogram)
    value = 0

    for i, x in enumerate(histogram):
        value += i * x
    value /= total

    error = 0
    for i, x in enumerate(histogram):
        error += x * (value - i) ** 2
    error /= total
    error = error ** 0.5
    
    return value, error

def get_color_histogram(histogram):
    """this function gets the color from a histogram"""

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

        hist = self.model.im.crop(self.box).histogram() #returns the histogram of the image
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
        """splits the image into a quad, compresses by 2^N"""

        l,t,r,b = self.box
        lr = l + (r-l)/2
        tb = t + (b-t)/2

        depth = self.depth + 1

        tl = Quad(self.model, (l,t,lr,tb), depth)
        tr = Quad(self.model, (lr,t,r,tb), depth)
        bl = Quad(self.model, (l,tb,lr,b), depth)
        br = Quad(self.model, (lr,tb,r,b), depth)

        self.children = (tl,tr,bl,br)
        
        return self.children

    def get_leaf_nodes(self, max_depth=None):
        if not self.children:
            return [self]
        if max_depth is not None and self.depth >= max_depth:
            return [self]
        result = []
        
        for child in self.children:
            result.extend(child.get_leaf_nodes(max_depth))

        return result


class ImageModel(object):

    def __init__(self, path):
        self.im = Image.open(path).convert('RGB')
        self.width, self.height = self.im.size
        self.heap = []
        self.root = Quad(self, (0,0, self.width, self.height), 0)
        self.error_sum = self.root.error * self.root.area
        self.push(self.root)

    
    @property #adds property version to quads
    def quads(self):
        return [x[-1] for x in self.heap]

    def average_error(self):
        return self.error_sum / (self.width * self.height)

    def push(self, quad):
        score = -quad.error * (quad.area ** AREA_POWER)
        heapq.heappush(self.heap, (quad.leaf, score, quad))

    def pop(self):
        return heapq.heappop(self.heap)[-1]

    def split(self):
        quad = self.pop()

        self.error_sum -= quad.error * quad.area
        children = quad.split()
        for child in children:
            self.push(child)
            self.error_sum += child.error * child.area

    def render(self, path, max_depth=None):
        """creates new image"""

        m = OUTPUT_SCALE
        dx, dy = (PADDING, PADDING)
        
        im = Image.new('RGB', (self.width * m, self.height * m), FILL_COLOR)

        draw = ImageDraw.Draw(im)
        draw.rectangle((0,0, self.width * m, self.height * m), FILL_COLOR)
        
        for quad in self.root.get_leaf_nodes(max_depth):
            l,t,r,b = quad.box
            box = (l*m + dx, t*m + dy, r*m - 1, b*m - 1)
            draw.rectangle(box, quad.color)

        del draw
        im.save(path, 'PNG')



