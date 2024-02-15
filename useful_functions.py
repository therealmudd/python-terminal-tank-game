import math

def sign(x):
    return 0 if x == 0 else 1 if x > 0 else -1

def dis(x1, y1, x2, y2):
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

def ang(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)

def lendir_x(len, dir):
    return math.cos(dir) * len

def lendir_y(len, dir):
    return math.sin(dir) * len         

def remap(value, istart, istop,  ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))