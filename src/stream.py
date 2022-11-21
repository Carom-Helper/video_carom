import cv2

def draw_curve(img, line, color):
    for x, y in line:
        img = cv2.line(img, (int(x), int(y)), (int(x), int(y)), color, 1)
    """
    for i in range(1, len(line)):
        p1 = line[i-1]
        p2 = line[i]
        if abs(p1[0] - p2[0]) != 1:
            #print(p1, p2)
            pass
        else:
            img = cv2.line(img, p1, p2, color, 2)
    """
    return img



def draw_point(img, point, thickness, color):
    x, y = point
    x = int(x)
    y = int(y)
    return cv2.line(img, (x, y), (x, y), color, thickness)



def draw_List(img, ball_list, thickness, color):
    for b in ball_list:
        img = draw_point(img, (b.x, b.y), thickness, color)
    return img



def readimgs(cap):
    imgs = []
    ret, img = cap.read()
    while ret:
        imgs.append(img)
        ret,img = cap.read()
    return imgs

def readimg(cap):
    ret, img = cap.read()
    return img if ret else None



def draw_balls(img, cue, t1, t2, c_color, t1_color, t2_color, thickness):
    img = draw_List(img, cue, thickness, c_color)
    img = draw_List(img, t1, thickness, t1_color)
    img = draw_List(img, t2, thickness, t2_color)
    return img



def draw_ball_trace(img, ball, color, thickness, frame):
    i=0
    while i < len(ball.modified_ball_list) and ball.modified_ball_list[i].fr <= frame:
        img = draw_point(img, (ball.modified_ball_list[i].x, ball.modified_ball_list[i].y), thickness, color)
        i+=1
    return img



def draw_edge(img, cshline, m):
    for csh in cshline:
        img = cv2.line(img, (int(csh[0][0]), int(csh[0][1])), (int(csh[1][0]), int(csh[1][1])), (255,0,0), 2)

    img = cv2.line(img, (int(cshline[0][0][0]-m), int(cshline[0][0][1]+m)), (int(cshline[1][0][0]+m), int(cshline[1][0][1]+m)), (255,0,0), 1)
    img = cv2.line(img, (int(cshline[1][0][0]+m), int(cshline[1][0][1]+m)), (int(cshline[2][0][0]+m), int(cshline[2][0][1]-m)), (255,0,0), 1)
    img = cv2.line(img, (int(cshline[2][0][0]+m), int(cshline[2][0][1]-m)), (int(cshline[3][0][0]-m), int(cshline[3][0][1]-m)), (255,0,0), 1)
    img = cv2.line(img, (int(cshline[3][0][0]-m), int(cshline[3][0][1]-m)), (int(cshline[0][0][0]-m), int(cshline[0][0][1]+m)), (255,0,0), 1)
    return img