import numpy as np
import warnings
import math
warnings.simplefilter('ignore', np.RankWarning)

def calc_y(x, coefficients):
    y = coefficients[0] * x * x + coefficients[1] * x + coefficients[2]
    return y

def calc_y_prime(x, coefficients):
    y_prime = 2 * coefficients[0] * x + coefficients[1]
    return y_prime

def get_middle_point(xs, coefficients):
    x_min = int(min(xs))
    x_max = int(max(xs))
    start_y_prime = calc_y_prime(x_min,coefficients)
    end_y_prime = calc_y_prime(x_max, coefficients)

    target_y_prime = (start_y_prime + end_y_prime)/2
    min_prime = abs(target_y_prime - start_y_prime)
    middle = x_min
    for i in range(x_min+1, x_max):
        y_prime = calc_y_prime(i, coefficients)
        if min_prime > abs(target_y_prime - y_prime):
            min_prime = abs(target_y_prime - y_prime)
            middle = i
    return middle

def curve_fit(xs, ys):
    coefficients = np.polyfit(xs, ys, 2)
    return coefficients

def curve_fit2(xs, ys):
    coefficients = curve_fit(xs, ys)
    x_middle = get_middle_point(xs, coefficients)
    y_middle = calc_y(x_middle, coefficients)

    xs2 = np.array([xs[0], x_middle, xs[-1]])
    ys2 = np.array([ys[0], y_middle, ys[-1]])

    coefficients2 = curve_fit(xs2, ys2)
    return coefficients2


def make_curve(ball_list):
    if len(ball_list) < 2:
        return []
    points = []
    for b in ball_list:
        points.append((b.x, b.y))
    start = points[0]
    end = points[-1]
    vector = (end[0] - start[0], end[1] - start[1])
    theta = math.pi/2 - math.atan2(vector[0], vector[1])

    transList = T_R_origin(points, start, theta)

    line = []

    xs, ys = [], []
    for b in transList:
        xs.append(b[0])
        ys.append(b[1])
    coefficients2 = curve_fit2(xs, ys)

    x_min = int(min(xs))
    x_max = int(max(xs))


    for i in range(x_min, x_max):
        line.append((i, int(calc_y(i, coefficients2))))
    
    lineList = R_T_reverse(line, start, theta)
    return lineList



def T_R_origin(ball_list, start, theta):
    t = np.array([[1, 0, 0], [0, 1, 0], [-start[0], -start[1], 1]])
    r = np.array([[math.cos(-theta), math.sin(-theta), 0], [-math.sin(-theta), math.cos(-theta), 0], [0, 0, 1]])
    transList = []
    for b in ball_list:
        v = np.array([b[0], b[1], 1])
        
        trans_v = v @ t @ r
        transList.append((trans_v[0], trans_v[1]))
    return transList



def R_T_reverse(ball_list, start, theta):
    r_r = np.array([[math.cos(theta), math.sin(theta), 0], [-math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
    t_r = np.array([[1, 0, 0], [0, 1, 0], [start[0], start[1], 1]])
    transList = []
    for b in ball_list:
        v = np.array([b[0], b[1], 1])
        
        trans_v = v @ r_r @ t_r
        transList.append((trans_v[0], trans_v[1]))
    return transList