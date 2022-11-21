from bagreader import bag_reader
from balltracker import make_line
from predict import event_predict
from pointmodify import modify_soft, modify_hard
from stream import draw_point, draw_ball_trace, draw_edge, draw_curve
from cvtCoord import cvtCoord, cvtball, cvtline, cvtimgs, make_pers
import cv2

def ballPredictor(ball_bags, edges, width, imgs):
    #set margin
    ball_margin = 26 * width / 1920
    csh_margin = 20 * width / 1920
    ball_radius = 13 * width / 1920

    #bag reader
    cue, tar1, tar2, cshline = bag_reader(ball_bags, edges)

    #modify soft
    cue.modified_ball_list = modify_soft(cue.ball_list)
    tar1.modified_ball_list = modify_soft(tar1.ball_list)
    tar2.modified_ball_list = modify_soft(tar2.ball_list)

    #event_predict
    event_list = event_predict(cue, tar1, tar2, cshline, ball_margin, csh_margin)

    #modify hard
    cue_tar1, cue_tar2, cshList = modify_hard(cue, tar1, tar2, event_list, cshline, ball_radius)

    #make line
    cue_line = make_line(cue)
    tar1_line = make_line(tar1)
    tar2_line = make_line(tar2)

    #cvt
    pers = make_pers(cshline)
    imgs = cvtimgs(imgs, pers)

    cvtball(cue, pers)
    cvtball(tar1, pers)
    cvtball(tar2, pers)

    e1 = cvtCoord(cshline[0][0][0], cshline[0][0][1], pers)
    e1 = (int(e1[0]), int(e1[1]))
    
    e2 = cvtCoord(cshline[1][0][0], cshline[1][0][1], pers)
    e2 = (int(e2[0]), int(e2[1]))
    
    e3 = cvtCoord(cshline[2][0][0], cshline[2][0][1], pers)
    e3 = (int(e3[0]), int(e3[1]))
    
    e4 = cvtCoord(cshline[3][0][0], cshline[3][0][1], pers)
    e4 = (int(e4[0]), int(e4[1]))
    cshline = ((e1,e2), (e2,e3), (e3,e4), (e4,e1))

    cue_line = cvtline(cue_line, pers)
    tar1_line = cvtline(tar1_line, pers)
    tar2_line = cvtline(tar2_line, pers)

    # draw imgs
    draw_imgs = []
    i = 0
    while i < len(imgs):
        img = imgs[i].copy()

        #img = PerspecTrans(img, [csh_origin[0][0],csh_origin[1][0],csh_origin[2][0],csh_origin[3][0]])

        #draw img
        img = draw_edge(img, cshline, int(csh_margin))
        img = draw_edge(img, cshline, int(ball_radius))

        img = draw_curve(img, cue_line, (255, 255, 255))
        img = draw_curve(img, tar1_line, (0, 0, 255))
        img = draw_curve(img, tar2_line, (0, 255, 255))

        img = draw_ball_trace(img, cue, (255, 255, 255), 3, i)
        img = draw_ball_trace(img, tar1, (0, 0, 255), 3, i)
        img = draw_ball_trace(img, tar2, (0, 255, 255), 3, i)

        for e in event_list:
            event1 = (e[0].x, e[0].y)
            img = draw_point(img, event1, 3, (0,128,255))
            if e[1] is not None:
                event2 = (e[1].x, e[1].y)
                img = draw_point(img, event1, 3, (128,255,0))
                img = draw_point(img, event2, 3, (128,255,0))
                img = cv2.line(img, (int(event1[0]), int(event1[1])), (int(event2[0]), int(event2[1])), (128,255,0), 1)
        
        draw_imgs.append(img)
        i+=1

    #event_list to sring
    event_str = ''
    event_str += f'{cue.modified_ball_list[0].fr}, InitialState, '
    event_str += f'({int(cue.modified_ball_list[0].x)},{int(cue.modified_ball_list[0].y)}), '
    event_str += f'({int(tar1.modified_ball_list[0].x)},{int(tar1.modified_ball_list[0].y)}), '
    event_str += f'({int(tar2.modified_ball_list[0].x)},{int(tar2.modified_ball_list[0].y)})\n'
    for e in event_list: 
        obj1_id = e[3]
        if obj1_id == 5:
            obj1 = "CueBall"
        elif obj1_id == 6:
            obj1 = "ObjectBall1"
        elif obj1_id == 7:
            obj1 = "ObjectBall2"
        else:
            obj1 = "Table"

        obj2_id = e[4]
        if obj2_id == 5:
            obj2 = "CueBall"
        elif obj2_id == 6:
            obj2 = "ObjectBall1"
        elif obj2_id == 7:
            obj2 = "ObjectBall2"
        else:
            obj2 = "Table"
        o1_x = e[0].x
        o1_y = e[0].y
        event_str += f'{e[0].fr}, {obj1}, {obj2}, ({int(o1_x)},{int(o1_y)})'
        if obj2 != "Table":
            o2_x = e[1].x
            o2_y = e[1].y
            event_str += f', ({int(o2_x)},{int(o2_y)})'
        event_str += f'\n'
    cue_last_frame = cue.modified_ball_list[-1].fr
    cue_last_idx = cue.find_index(cue_last_frame)
    tar1_last_frame = tar1.modified_ball_list[-1].fr
    tar1_last_idx = tar1.find_index(tar1_last_frame)
    tar2_last_frame = tar2.modified_ball_list[-1].fr
    tar2_last_idx = tar2.find_index(tar2_last_frame)

    event_str += f'{cue.modified_ball_list[cue_last_idx].fr}, EndState, '
    event_str += f'({int(cue.modified_ball_list[cue_last_idx].x)},{int(cue.modified_ball_list[cue_last_idx].y)}), '
    event_str += f'({int(tar1.modified_ball_list[tar1_last_idx].x)},{int(tar1.modified_ball_list[tar1_last_idx].y)}), '
    event_str += f'({int(tar2.modified_ball_list[tar2_last_idx].x)},{int(tar2.modified_ball_list[tar2_last_idx].y)})\n'

    return event_str, draw_imgs
