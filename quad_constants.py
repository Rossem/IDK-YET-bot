#defining three optional modes for drawing quad images

MODE_RECT = 1
MODE_ELLIPSE = 2
MODE_RND_RECT = 3


MODE = MODE_RECT

ITERATIONS = 1024 #2^N of how small to decompose the image
LEAF_SIZE = 4
PADDING = 1
FILL_COLOR = (0,0,0)
SAVE_FRAMES = False #save decomposition frames
ERROR_RATE = 0.5
AREA_POWER = 0.25
OUTPUT_SCALE = 1
