import os, time, math, textwrap

'''
SOME TERMINOLOGY:
    grid   - 2D list of characters
    canvas - a grid of characters displayed in the terminal
    pixel  - a single character in the canvas
    fill   - the pixel inside some shape
    stroke - the pixel that is the outline of some shape
    RGB    - represents a colour by the amount of red, green, blue it contains
    HSV    - represents a colour by its hue, saturation and value
    sprite - a grid of pixels smaller than the canvas (usually static)

NOTES:
    - To make each cell in the grid of the canvas roughly square shaped, 
      a space gets added to the front of a character
    - The coordinates of the top left corner of the canvas is (0, 0)
    - The coordinates of the bottom right corner of the canvas (width-1, height-1)
    - RGB values range from 0 to 255
    - In HSV:
      > hue ranges from 0 to 360
      > saturation ranges from 0 to 100
      > value ranges from 0 to 100

    - Hope this makes sense. :)
''' 

# BASIC COLOURS #

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AQUA = (255, 255, 0)
YELLOW = (255, 255, 0)
PINK = (255, 0, 255)

# CANVAS CLASS #

class Canvas():
    def __init__(self, width, height, border="*", border_colour=WHITE, fill=" ", fill_colour=WHITE):
        self.width = int(width)
        self.height = int(height)
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.center = (self.center_x, self.center_y)
        self.border_colour = border_colour
        self.border = coloured(border_colour, border)
        self.fill = coloured(fill_colour, fill)
        self.grid = [[" "+border if x in [0, self.width-1] or y in [0, self.height-1] else " " + fill \
            for x in range(self.width)] for y in range(self.height)]

    def hsv(self, r, g, b):
        '''Converts a colour from RGB to HSV'''
        return hsv(r, g, b)
    
    def rgb(self, h, s, v):
        '''Converts a colour from HSV to RGB'''
        return rgb(h, s, v)

    def coloured(self, rgb, pixel="*"):
        '''Returns a coloured pixel'''
        return coloured(rgb, pixel)

    def set(self, x, y, pixel="*", colour=WHITE):
        '''Sets a pixel at a particular position on the canvas' grid'''
        pixel = coloured(colour, pixel)
        if x in range(self.width) and y in range(self.height):
            self.grid[y][x] = " " + pixel

    def override(self, x, y, fill="  ", colour=WHITE):
        '''Overrides the enter cell of the canvas' grid with some fill'''
        fill = (fill + "  ")[:2]
        fill = coloured(colour, fill)
        if x in range(self.width) and y in range(self.height):
            self.grid[y][x] = fill

    def get(self, x, y):
        '''Gets the pixel at some position on the canvas'''
        return self.grid[y][x][-1]
    
    def draw_pixel(self, x, y, pixel="*", colour=WHITE):
        '''Draws a single pixel at some position'''
        pixel = coloured(colour, pixel)
        self.set(round(x), round(y), pixel)

    def draw_text(self, x, y, text, colour=WHITE):
        '''Draws some text at some position'''
        dx = 0
        for pair in textwrap.wrap(text, 2, drop_whitespace=False):
            self.override(round(x + dx), round(y), pair, colour)
            dx += 1

    def draw_line(self, x1, y1, x2, y2, stroke="*", colour=WHITE):
        '''Draws a line between two points'''
        stroke = coloured(colour, stroke)
        d = dis(x1, y1, x2, y2)
        a = ang(x1, y1, x2, y2)

        px, py = x1, y1
        for _ in range(0, round(d)+1):
            self.set(round(px), round(py), stroke)
            px += lendir_x(1, a)
            py += lendir_y(1, a)

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, stroke="*", colour=WHITE):
        '''Draws a triangle given three points'''
        stroke = coloured(colour, stroke)
        self.draw_line(x1, y1, x2, y2, stroke)
        self.draw_line(x1, y1, x3, y3, stroke)
        self.draw_line(x2, y2, x3, y3, stroke)

    def draw_rectangle(self, x, y, wid, hei, stroke="*", colour=WHITE):
        '''Draw a rectangle with its top left corner at some point'''
        stroke = coloured(colour, stroke)
        self.draw_line(x, y, x+wid, y, stroke)
        self.draw_line(x, y, x, y+hei, stroke)
        self.draw_line(x+wid, y, x+wid, y+hei, stroke)
        self.draw_line(x, y+hei, x+wid, y+hei, stroke)

    def draw_square(self, x, y, wid, stroke="*", colour=WHITE):
        '''Draws a square with its top left corner at some point'''
        stroke = coloured(colour, stroke)
        self.draw_rectangle(x, y, wid, wid, stroke)

    def draw_arc(self, x, y, radius, start_angle, end_angle, stroke="*", colour=WHITE):
        '''Draws an arc centered at some position with some radius'''
        stroke = coloured(colour, stroke)
        start_angle += 180
        end_angle += 180
        for angle in range(start_angle, end_angle+1):
            dx = round(x) + lendir_x(radius, math.radians(angle))
            dy = round(y) + lendir_y(radius, math.radians(angle))
            self.set(round(dx), round(dy), stroke)

    def draw_circle(self, x, y, radius, stroke="*", colour=WHITE):
        '''Draws a circle centered at position with some radius'''
        self.draw_arc(x, y, radius, 0, 360, stroke, colour)

    def draw_polygon(self, points, stroke="*", colour=WHITE):
        '''Takes a list of points (list of x and y) and draws a shape from them'''
        stroke = coloured(colour, stroke)
        for point, i in enumerate(points):
              self.draw_line(point[0], point[1], points[(i+1)%len(points)][0], points[(i+1)%len(points)][1], stroke)

    def draw_sprite(self, x, y, sprite, transparent=False):
        '''Takes a grid of pixels'''
        for sy in range(len(sprite)):
            for sx in range(len(sprite[0])):
                if transparent and sprite[sy][sx] == " ": continue
                self.set(round(x+sx), round(y+sy), sprite[sy][sx])

    def reset(self, fill=" "):
        '''Clears the contents of the canvas'''
        self.grid = [[" "+self.border if x in [0, self.width-1] or y in [0, self.height-1] else " " + self.fill \
            for x in range(self.width)] for y in range(self.height)]
        
    def clear(self, fill=" "):
        '''Clears the entire terminal and contents of the canvas'''
        self.reset(fill)
        if os.name == "nt":
            _ = os.system("cls")
        else:
            _ = os.system("clear")

    def show(self, sleep=0):
        '''Displays the canvas in the terminal'''
        for y in range(self.height):
            for x in range(self.width):
                print(self.grid[y][x], end="")
            print("")
        time.sleep(sleep)

# USEFUL FUNCTIONS #

def dis(x1, y1, x2, y2):
    '''Finds the distance between two points'''
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

def ang(x1, y1, x2, y2):
    '''Finds the angle (in radians) between two points'''
    return math.atan2(y2 - y1, x2 - x1)

def lendir_x(len, dir):
    '''Gets the x-component of a vector of length `len` in direction `dir`'''
    return math.cos(dir) * len

def lendir_y(len, dir):
    '''Gets the y-component of a vector of length `len` in direction `dir`'''
    return math.sin(dir) * len         

def remap(value, in_min, in_max, out_min, out_max):
    '''Scales some value on a scale (in_min, in_max) to some other scale (out_min, out_max)'''
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))

def hsv(r, g, b):
    '''Converts a colour from rgb to hsv'''
    r_ = r/255
    g_ = g/255
    b_ = b/255

    cmax = max(r_, g_, b_)
    cmin = min(r_, g_, b_)
    delta = cmax - cmin

    if delta == 0:
        h = 0
    elif cmax == r_:
        h = 60 * ((g_ - b_)/delta % 6)
    elif cmax == g_:
        h = 60 * ((b_ - r_)/delta + 2)
    elif cmax == b_:
        h = 60 * ((r_ - g_)/delta + 4)
    
    if cmax == 0:
        s = 0
    else:
        s = delta / cmax
    
    v = cmax
    return h, s, v

def rgb(h, s, v):
    '''Converts a color from RGB to HSV'''
    h, s, v = h % 360, s * 0.01, v * 0.01
    c = v * s
    x = c * (1 - abs((h/60) % 2 - 1))
    m = v - c

    r_, g_, b_ = [
        (c, x, 0),
        (x, c, 0),
        (0, c, x),
        (0, x, c),
        (x, 0, c),
        (c, 0, x)
    ][int(remap(h, 0, 360, 0, 5))]

    r, g, b = (r_+m)*255, (g_+m)*255, (b_+m)*255
    return r, g, b

def coloured(rgb: tuple, fill="*"):
    '''Returns a coloured pixel'''
    r, g, b = map(int, rgb)
    return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(r, g, b, fill)


canvas = Canvas(20, 10)
text = "Hello, canvas!"
canvas.draw_text(10 - len(text)//4, canvas.height//2, text)
print()
canvas.show()
print()