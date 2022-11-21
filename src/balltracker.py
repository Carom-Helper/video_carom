import math
import numpy as np
from curve import make_curve

def get_vector(b_curr, b_prev):
    v = [b_curr.x - b_prev.x, b_curr.y - b_prev.y]
    return v



def norm(vector):
    length = (vector[0]**2 + vector[1]**2)**0.5
    if length > 0:
        norm_vector = [vector[0] / length, vector[1] / length]
    else:
        norm_vector = [0, 0]
    return norm_vector



def get_degree(vector_in, vector_out):
    nv_in = norm(vector_in)
    nv_out = norm(vector_out)
    rad1 = math.atan2(nv_in[0], nv_in[1])
    rad2 = math.atan2(nv_out[0], nv_out[1])
    deg1 = (rad1 * 180) / math.pi
    deg2 = (rad2 * 180) / math.pi

    deg = abs(deg1 - deg2)
    return deg



def find_ini(ball_list):
    i = 1
    while i < len(ball_list):
        if ball_list[i].move:
            break
        i += 1
    return i - 1



def point_dist(obj1, obj2):
    return ((obj2.x-obj1.x)**2 + (obj2.y-obj1.y)**2)**0.5



def get_dist(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5



def line_dist(b, line):
    sx = line[0][0] #start x
    sy = line[0][1] #start y
    ex = line[1][0] #end x
    ey = line[1][1] #end y

    line_length = ((ex-sx)**2 + (ey-sy)**2)**0.5
    absdot = abs(np.dot((b.x-sx, b.y-sy), (ex-sx, ey-sy)))
    if absdot > 0:
        absdot = absdot**0.5

    if line_length > absdot:
        line_distance = abs((ex - sx) * (sy - b.y) - (sx - b.x) * (ey - sy)) / line_length if line_length > 0 else 0
    else:
        line_distance = min(((sx-b.x)**2 + (sy-b.y)**2)**0.5,((ex-b.x)**2 + (ey-b.y)**2)**0.5)
    return line_distance



def line_dist_point(b, line):
    sx = line[0][0] #start x
    sy = line[0][1] #start y
    ex = line[1][0] #end x
    ey = line[1][1] #end y

    line_length = ((ex-sx)**2 + (ey-sy)**2)**0.5
    absdot = abs(np.dot((b[0]-sx, b[1]-sy), (ex-sx, ey-sy)))
    if absdot > 0:
        absdot = absdot**0.5

    if line_length > absdot:
        line_distance = abs((ex - sx) * (sy - b[1]) - (sx - b[0]) * (ey - sy)) / line_length if line_length > 0 else 0
    else:
        line_distance = min(((sx-b[0])**2 + (sy-b[1])**2)**0.5,((ex-b[0])**2 + (ey-b[1])**2)**0.5)
    return line_distance



def is_cue(b1, b2):
    b1_ini = find_ini(b1.ball_list)
    b2_ini = find_ini(b2.ball_list)

    if b1_ini < b2_ini:
        return True
    elif b2_ini < b1_ini:
        return False

    v1 = get_vector(b1.ball_list[b1_ini+1], b1.ball_list[b1_ini])
    v1 = norm(v1)
    v_2to1 = get_vector(b2.ball_list[b2_ini], b1.ball_list[b1_ini])
    v_2to1 = norm(v_2to1)

    v2 = get_vector(b2.ball_list[b1_ini+1], b2.ball_list[b1_ini])
    v2 = norm(v2)
    v_1to2 = get_vector(b1.ball_list[b1_ini], b2.ball_list[b2_ini])
    v_1to2 = norm(v_1to2)

    rad1 = math.atan2(v1[0], v1[1])
    rad2 = math.atan2(v_2to1[0], v_2to1[1])
    deg_v1 = (rad1 * 180) / math.pi
    deg_v_2to1 = (rad2 * 180) / math.pi
    deg_b1_cue = abs(deg_v1 - deg_v_2to1)

    rad1 = math.atan2(v2[0], v2[1])
    rad2 = math.atan2(v_1to2[0], v_1to2[1])
    deg_v2 = (rad1 * 180) / math.pi
    deg_v_1to2 = (rad2 * 180) / math.pi
    deg_b2_cue = abs(deg_v2 - deg_v_1to2)

    if deg_b1_cue < deg_b2_cue:
        return True
    else:
        return False



def find_cue(b1, b2, b3):
    if is_cue(b1, b2) and is_cue(b1, b3):
        return (b1, b2, b3) if is_cue(b2, b3) else (b1, b3, b2)
    
    elif is_cue(b2, b1) and is_cue(b2, b3):
        return (b2, b1, b3) if is_cue(b1, b3) else (b2, b3, b1)
    
    elif is_cue(b3, b2) and is_cue(b3, b1):
        return (b3, b1, b2) if is_cue(b1, b2) else (b3, b2, b1)



def make_line(ball):
    ball_line = []

    b_part = []
    b_start_idx = find_ini(ball.modified_ball_list)
    for b_end in ball.event_frame:
        b_end_idx = ball.find_index(b_end)
        if b_start_idx > b_end_idx:
            break
        b_part = ball.modified_ball_list[b_start_idx:b_end_idx+1]

        line = make_curve(b_part)
        ball_line += line
        b_start_idx = b_end_idx
    return ball_line