import numpy as np
from balltracker import get_vector, find_ini, point_dist, line_dist, get_degree

def find_collision_soft(fixed_ball_list):
    col_list = []
    
    iniframe = find_ini(fixed_ball_list)
    col_list.append(fixed_ball_list[iniframe])

    for i in range(1, len(fixed_ball_list)-1):
        if collision_check_soft(fixed_ball_list[i+1], fixed_ball_list[i], fixed_ball_list[i-1]):
            col_list.append(fixed_ball_list[i])

    col_list.append(fixed_ball_list[-1])
    return col_list



def collision_check_soft(b_post, b_curr, b_prev):
    angle_limit = 15

    if not b_curr.move and not b_post.move:
        return False

    vector_in = np.array(get_vector(b_curr, b_prev))
    vector_out = np.array(get_vector(b_post, b_curr))

    deg = get_degree(vector_in, vector_out)
    result = deg if deg < 180 else 360 - deg

    return True if result > angle_limit else False



def nearest_b(cue, tar, last_event_idx, ball_margin):
    if cue.last_event_obj == tar.id and tar.last_event_obj == cue.id:
        return None, None, None, None, None, None
    prev_moved = None
    try:
        prev_cue = cue.modified_ball_list[last_event_idx]
        prev_tar = tar.modified_ball_list[last_event_idx]
    except:
        print("nearest_b error index ", last_event_idx)
        return None, None, None, None, None, None
    count = 0
    prev_dist = 0
    prev_cv = None
    prev_tv = None
    for c, t in zip(cue.modified_ball_list[last_event_idx+1:], tar.modified_ball_list[last_event_idx+1:]):
        curr_cv = get_vector(c, prev_cue)
        curr_tv = get_vector(t, prev_tar)

        if not prev_tar.move:
            line = ((c.x, c.y), (prev_cue.x, prev_cue.y))
            curr_dist = line_dist(prev_tar, line)
        elif not prev_cue.move:
            line = ((t.x, t.y), (prev_tar.x, prev_tar.y))
            curr_dist = line_dist(prev_cue, line)
        else:
            curr_dist = point_dist(c, t)
        
        curr_moved = curr_dist - prev_dist
        ball_margin_weighted = ball_margin - min(prev_moved if prev_moved is not None else 0, 0)

        if prev_moved == None:
            pass
        else:
            #targetball stop=>move
            if not prev_tar.move and t.move:
                if prev_dist <= ball_margin_weighted * 1.4:
                    return prev_cue, prev_tar, last_event_idx + count, cue.id, tar.id, prev_dist
            
            #cueball move & targetball move
            elif prev_moved * curr_moved <= 0 and prev_moved < 0 and t.move:
                if prev_dist <= ball_margin_weighted:
                    if get_degree(prev_cv, curr_cv) > 15 or get_degree(prev_tv, curr_tv) > 15:
                        return prev_cue, prev_tar, last_event_idx + count, cue.id, tar.id, prev_dist

        prev_moved = curr_moved
        prev_cue = c
        prev_tar = t
        prev_dist = curr_dist
        prev_cv = curr_cv
        prev_tv = curr_tv
        count += 1
    return None, None, None, None, None, None



def nearest_csh(ball, cshline, last_event_idx, csh_margin):
    prev_moved = [None, None, None, None]
    try:
        prev_b = ball.modified_ball_list[last_event_idx]
    except:
        print("nearest_csh error index ", last_event_idx)
        return None, None, None, None, None, None
    count = 0
    for b in ball.modified_ball_list[last_event_idx+1:]:
        for i in range(1, 5):
            if ball.last_event_obj == i:
                pass
            prev_dist = line_dist(prev_b, cshline[i-1])
            curr_dist = line_dist(b, cshline[i-1])
            moved = curr_dist - prev_dist
            csh_margin_weighted = csh_margin - min(prev_moved[i-1] if prev_moved[i-1] is not None else 0, 0)
            
            if prev_moved[i-1] == None:
                prev_moved[i-1] = moved
            else:
                if prev_moved[i-1] * moved <= 0 and prev_moved[i-1] < 0 and prev_dist <= csh_margin_weighted:
                    if ball.last_event_obj is not i or ball.last_csh_dist > prev_dist:
                        prev_moved[i-1] = moved
                        last_event_csh = i
                        return prev_b, None, last_event_idx + count, ball.id, last_event_csh, prev_dist
                    
                    else:
                        prev_moved[i-1] = moved
                else:
                    prev_moved[i-1] = moved
            
        prev_b = b
        count += 1
    return None, None, None, None, None, None



def event_predict(cue, tar1, tar2, cshline, ball_margin, csh_margin):
    event_list = []
    last_event_idx = find_ini(cue.ball_list)-1

    while True:
        possible_event_list = []
        possible_event_list.append((nearest_csh(cue, cshline, last_event_idx, csh_margin)))
        possible_event_list.append((nearest_csh(tar1, cshline, last_event_idx, csh_margin)))
        possible_event_list.append((nearest_csh(tar2, cshline, last_event_idx, csh_margin)))
        possible_event_list.append((nearest_b(cue, tar1, last_event_idx, ball_margin)))
        possible_event_list.append((nearest_b(cue, tar2, last_event_idx, ball_margin)))
        possible_event_list.append((nearest_b(tar1, tar2, last_event_idx, ball_margin)))

        while (None, None, None, None, None, None) in possible_event_list:
            possible_event_list.remove((None, None, None, None, None, None))

        if len(possible_event_list) == 0:
            return event_list

        possible_event_list.sort(key=lambda x:x[2])
        
        for next_event in possible_event_list:
            last_event_idx = next_event[2]
            if last_event_idx > possible_event_list[0][2]:
                last_event_idx = possible_event_list[0][2]
                break

            if next_event[3] == 6 and next_event[1] == None and len(tar1.event_frame) == 0:
                continue
            if next_event[3] == 7 and next_event[1] == None and len(tar2.event_frame) == 0:
                continue

            if next_event[4] in range(4):
                for b in (cue, tar1, tar2):
                    if b.id == next_event[3] and b.last_event_obj == next_event[4]:
                        i = len(event_list)-1
                        while i >=0 and event_list[i][3] != next_event[3]:
                            i -= 1
                        if i < 0:
                            break
                        else:
                            del event_list[i]

            event_list.append(next_event)
            
            for b in (cue, tar1, tar2):
                b.add_event(next_event[3], next_event[4], next_event[0].fr, next_event[5])
                if next_event[1] is not None:
                    b.add_event(next_event[4], next_event[3], next_event[1].fr, next_event[5])