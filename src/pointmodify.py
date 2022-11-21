from curve import curve_fit2, calc_y
from predict import find_collision_soft
from balltracker import get_vector, line_dist_point, point_dist, line_dist, get_dist
from caromobject import Binfo

def modify_miss(fixed, index, miss_len):
    start_point = fixed[index]
    end_point = fixed[index+1]
    start_frame = start_point.fr
    start_index = index

    fixed_miss = []
    fixed_miss += fixed
    xs = []
    ys = []
    for b in fixed_miss:
        xs.append(b.x)
        ys.append(b.y)
    #current curve
    coefficients = curve_fit2(xs, ys)

    #generate point (x coord linear interpolation)
    for i in range(miss_len):
        #generate x, y
        if start_point.move and not end_point.move and start_index > 0: #start = move / end = stop
            generated_x = int(start_point.x + (start_point.x - fixed[start_index-1].x) * (i+1))
            if (end_point.x - generated_x) * (end_point.x - start_point.x) < 0:
                generated_x = end_point.x

        elif not start_point.move and end_point.move and len(fixed) > start_index + 2: #start = stop / end = move
            generated_x = int(end_point.x - (fixed[start_index+2].x - end_point.x) * (miss_len-i))
            if (generated_x - start_point.x) * (end_point.x - start_point.x) < 0:
                generated_x = start_point.x

        else:
            generated_x = int(start_point.x + (end_point.x - start_point.x) * (i+1) / (miss_len+1))
            
        generated_y = int(calc_y(generated_x, coefficients))
        
        #generate point
        generated_point = Binfo(start_frame + i + 1, generated_x, generated_y)
        
        #insert point
        fixed_miss.insert(index + 1, generated_point)

        t = index
        margin = 2.24
        dist = point_dist(fixed_miss[index + 1], fixed_miss[t])
        
        while t > 0:
            if fixed_miss[t].move == True or dist > margin:
                break
            else:
                t -= 1
                dist = point_dist(fixed_miss[index + 1], fixed_miss[t])
        fixed_miss[index + 1].move = False if dist <= margin else True

        index += 1

    return fixed_miss



def modify_soft(ball_list):
    colList = find_collision_soft(ball_list)

    modified_ball_list = []

    col_start = 0
    col_end = 1
    while col_end < len(ball_list):
        if ball_list[col_end] in colList:
            fixed_miss = ball_list[col_start:(col_end+1)]
            i = 0

            while fixed_miss[i].fr < fixed_miss[-1].fr:
                miss_len = fixed_miss[i+1].fr - fixed_miss[i].fr - 1
                if miss_len > 0:
                    fixed_miss = modify_miss(fixed_miss, i, miss_len)
                i += 1

            fixed_miss += fixed_miss

            for m_b in fixed_miss:
                if m_b not in modified_ball_list:
                    modified_ball_list.append(m_b)
            col_start = col_end
        col_end += 1
    
    return modified_ball_list



def modify_csh_point(ball, event_list, hit_frame, cshline, ball_radius):
    hit_idx = ball.find_index(hit_frame)
    hit_csh = None
    event_idx = None

    for e in event_list:
        if hit_frame == e[0].fr and ball.id == e[3] and e[1] is None:
            event_idx = event_list.index(e)
            hit_csh = event_list[event_idx][4]
            break

    only_csh = True
    for i in range(hit_idx-2, hit_idx+3):
        if not only_csh:
            break
        for e in event_list:
            if ball.modified_ball_list[i].fr > e[0].fr:
                break
            if ball.modified_ball_list[i].fr == e[0].fr and hit_csh != e[4]:
                only_csh = False
                break
    if only_csh:
        p1 = (ball.modified_ball_list[hit_idx-2].x, ball.modified_ball_list[hit_idx-2].y)
        p2 = (ball.modified_ball_list[hit_idx-1].x, ball.modified_ball_list[hit_idx-1].y)
        p3 = (ball.modified_ball_list[hit_idx].x, ball.modified_ball_list[hit_idx].y)
        p4 = (ball.modified_ball_list[hit_idx+1].x, ball.modified_ball_list[hit_idx+1].y)
        p5 = (ball.modified_ball_list[hit_idx+2].x, ball.modified_ball_list[hit_idx+2].y)
        csh_point1 = getCross(p1, p2, p3, p4)
        csh_point2 = getCross(p2, p3, p4, p5)
        
        xy = (hit_csh+1) % 2

        #1-2 / 3-4 cushion => csh_point.x is between p2.x, p3.x
        #2-3 / 4-1 cushion => csh_point.y is between p2.y, p3.y
        if csh_point1 is None or csh_point2 is None:
            return None

        if (csh_point1[xy] - p2[xy]) * (csh_point1[xy] - p3[xy]) <= 0:
            dist1 = get_dist(csh_point1, p2)
            dist2 = get_dist(csh_point1, p3)
            dist_criteria = get_dist(p2,p3) * 1.2
            dist = dist2 / (dist1 + dist2)
            if dist < dist_criteria and dist > 0.2 and dist < 0.8:
                dist = int(dist*10)/10
                csh_event = ball.insert_predict(hit_frame-dist, csh_point1[0], csh_point1[1], hit_idx)
                csh_event.move = True
                ball.update_csh_event(hit_frame, hit_frame-dist)
                event_list[event_idx] = (csh_event, None, event_list[event_idx][2], event_list[event_idx][3], event_list[event_idx][4])
            return csh_point1

        if (csh_point2[xy] - p3[xy]) * (csh_point2[xy] - p4[xy]) <= 0:
            dist1 = get_dist(csh_point2, p3)
            dist2 = get_dist(csh_point2, p4)
            dist_criteria = get_dist(p3,p4) * 1.2
            dist = dist1 / (dist1 + dist2)
            if dist < dist_criteria and dist > 0.2 and dist < 0.8:
                dist = int(dist*10)/10
                csh_event = ball.insert_predict(hit_frame+dist, csh_point2[0], csh_point2[1], hit_idx+1)
                csh_event.move = True
                ball.update_csh_event(hit_frame, hit_frame+dist)
                event_list[event_idx] = (csh_event, None, event_list[event_idx][2], event_list[event_idx][3], event_list[event_idx][4])
            return csh_point2

    else:
        p1 = None
        p2 = None
        pn = None
        reverse = False

        for i in range(hit_idx-2, hit_idx+2):
            p1_hit = False
            p2_hit = False

            for e in event_list:
                if ball.modified_ball_list[i].fr > e[0].fr:
                    break
                if ball.modified_ball_list[i].fr == e[0].fr and hit_csh != e[4]:
                    p1_hit = True
                    break
                if ball.modified_ball_list[i+1].fr == e[0].fr and hit_csh != e[4]:
                    p2_hit = True
                    break

            if not p1_hit and not p2_hit:
                if i < hit_idx:
                    p1 = ball.modified_ball_list[i].x, ball.modified_ball_list[i].y
                    p2 = ball.modified_ball_list[i+1].x, ball.modified_ball_list[i+1].y
                    pn = ball.modified_ball_list[i+2].x, ball.modified_ball_list[i+2].y

                else:
                    p1 = ball.modified_ball_list[i+2].x, ball.modified_ball_list[i+2].y
                    p2 = ball.modified_ball_list[i+1].x, ball.modified_ball_list[i+1].y
                    pn = ball.modified_ball_list[i].x, ball.modified_ball_list[i].y
                    reverse = True

                if i == hit_idx-2 or i == hit_idx+1:
                    dist_select = False
                else:
                    dist_select = True
                break

        if p1 is not None and p2 is not None:
            xs = [0, 1, 0, -1]
            ys = [1, 0, -1, 0]
            p3 = cshline[hit_csh-1][0][0] + ball_radius * xs[hit_csh-1], cshline[hit_csh-1][0][1] + ball_radius * ys[hit_csh-1]
            p4 = cshline[hit_csh-1][1][0] + ball_radius * xs[hit_csh-1], cshline[hit_csh-1][1][1] + ball_radius * ys[hit_csh-1]
            csh_point = getCross(p1, p2, p3, p4)
            csh_dist = line_dist(ball.modified_ball_list[hit_idx], cshline[hit_csh-1])
            new_csh_dist = line_dist_point(csh_point, cshline[hit_csh-1])
            
            dist1 = get_dist(csh_point, p2)
            dist2 = get_dist(csh_point, pn)
            dist_criteria = get_dist(p2, pn) * 1.2
            dist = (dist1 if dist_select else dist2) / (dist1 + dist2)
            
            if dist < dist_criteria and dist > 0.2 and dist <= 0.8 and new_csh_dist < csh_dist:
                dist = int(dist*10)/10
                new_hit_frmae = hit_frame+dist if reverse else hit_frame-dist
                csh_event = ball.insert_predict(new_hit_frmae, csh_point[0], csh_point[1], hit_idx)
                csh_event.move = True
                ball.update_csh_event(hit_frame, new_hit_frmae)
                event_list[event_idx] = (csh_event, None, event_list[event_idx][2], event_list[event_idx][3], event_list[event_idx][4])
            
                return csh_point
            else:
                return None



def modify_hit_point(cue, tar, event_list, cshline):
    cue_tar = None

    if len(tar.event_frame) > 1:
        #target 1st hit frame index
        t_idx = tar.find_index(tar.event_frame[0])
        t_fr = tar.modified_ball_list[t_idx].fr

        #target 2nd hit frame index
        tn_idx = tar.find_index(tar.event_frame[1])

        tar_hit = (tar.modified_ball_list[t_idx].x, tar.modified_ball_list[t_idx].y)
        tar_next_hit = (tar.modified_ball_list[tn_idx].x, tar.modified_ball_list[tn_idx].y)
        
        c_idx = cue.find_index(t_fr)
        
        cue_hit = (cue.modified_ball_list[c_idx].x, cue.modified_ball_list[c_idx].y)
        cue_next = (cue.modified_ball_list[c_idx+1].x, cue.modified_ball_list[c_idx+1].y)

        if cue.modified_ball_list[c_idx-1].move:
            cue_v = get_vector(cue.modified_ball_list[c_idx], cue.modified_ball_list[c_idx-1])
            cue_front = (cue_hit[0] + cue_v[0], cue_hit[1] + cue_v[1])
        else:
            cue_front = (cue.modified_ball_list[c_idx+1].x, cue.modified_ball_list[c_idx+1].y)

        cue_tar = cue_hit
        
        hit_front = getCross(cue_hit, cue_front, tar_hit, tar_next_hit)
        ret, percent = check_cross(cue_hit, cue_front, cue_next, hit_front)
        if ret:
            #update event
            cue_tar = hit_front
            new_cue_frame = cue.modified_ball_list[c_idx].fr+ percent * (cue.modified_ball_list[c_idx+1].fr - cue.modified_ball_list[c_idx].fr)
            new_cue_index = c_idx + (1 if new_cue_frame <= cue.modified_ball_list[c_idx+1].fr else 2)

            new_cue = cue.insert_predict(new_cue_frame, cue_tar[0], cue_tar[1], new_cue_index)
            cue.modified_ball_list[c_idx+1].move = True
            cue.event_frame[cue.event_frame.index(t_fr)] = new_cue_frame

            #update event_list
            new_tar_frame = new_cue_frame
            new_tar_index = t_idx + (1 if new_tar_frame <= tar.modified_ball_list[t_idx+1].fr else 2)

            new_tar = tar.insert_predict(new_tar_frame, tar.modified_ball_list[t_idx].x, tar.modified_ball_list[t_idx].y, new_tar_index)
            tar.event_frame[tar.event_frame.index(t_fr)] = new_tar_frame
            event_update = False
            for i in range(len(event_list)):
                if event_list[i][1] is not None and event_list[i][3] == cue.id and event_list[i][4] == tar.id and event_list[i][1].fr == t_fr:
                    event_list[i] = (new_cue, new_tar, c_idx+1, event_list[i][3], event_list[i][4])
                    event_update = True
                    break

            #update csh event
            if event_update:
                for i in range(len(event_list)):
                    if event_list[i][1] is None and (event_list[i][0].fr > int(new_cue.fr-1) and event_list[i][0].fr < int(new_cue.fr+2)):
                        csh_id = event_list[i][4]
                        curr_dist = line_dist(cue.modified_ball_list[c_idx], cshline[csh_id-1])
                        new_dist = line_dist(new_cue, cshline[csh_id-1])
                        if curr_dist >= new_dist:
                            event_list[i] = (new_cue, None, c_idx+1, event_list[i][3], event_list[i][4])
                        break

    return cue_tar



def modify_hard(cue, tar1, tar2, event_list, cshline, ball_radius):
    cue.event_frame.append(cue.modified_ball_list[-1].fr)
    tar1.event_frame.append(tar1.modified_ball_list[-1].fr)
    tar2.event_frame.append(tar2.modified_ball_list[-1].fr)
    
    cshList = []

    i = 0
    while i < len(event_list):
        for ball in (cue, tar1, tar2):
            if event_list[i][3] == ball.id and event_list[i][1] is None:
                csh = modify_csh_point(ball, event_list, event_list[i][0].fr ,cshline, ball_radius)
                if csh is not None:
                    cshList.append(csh)
        i+=1

    #cue_tar1 = None
    cue_tar1 = modify_hit_point(cue, tar1, event_list, cshline)
    cue_tar2 = modify_hit_point(cue, tar2, event_list, cshline)
    return cue_tar1, cue_tar2, cshList



def getCross(p1, p2, p3, p4):
    if ((p1[0]-p2[0])*(p3[1]-p4[1]) - (p1[1]-p2[1])*(p3[0]-p4[0])) != 0:
        x = ((p1[0]*p2[1] - p1[1]*p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0]-p2[0])*(p3[1]-p4[1]) - (p1[1]-p2[1])*(p3[0]-p4[0]))
        y = ((p1[0]*p2[1] - p1[1]*p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0]-p2[0])*(p3[1]-p4[1]) - (p1[1]-p2[1])*(p3[0]-p4[0]))
        return (x, y)
    else:
        return None



def check_cross(cue_hit, cue_front, cue_next, cross):
    if (cross[0] - cue_hit[0]) * (cross[0] - cue_front[0]) <= 0 or (cross[1] - cue_hit[1]) * (cross[1] - cue_front[1]) <= 0:
        dist1 = get_dist(cross, cue_hit)
        dist2 = ((cross[0]-cue_next[0])**2 + (cross[1]-cue_next[1])**2)**0.5
        percent = dist1 / (dist1 + dist2)
        if percent > 0.2 :#and percent < 0.8:
            return True, int(percent*10)/10
    
    return False, 0