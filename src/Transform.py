import cv2
import numpy as np

def PerspecTrans(img, points):
    pts = np.zeros((4, 2), dtype=np.float32)
    for i in range(4):
        pts[i] = points[i]
    
    sm = pts.sum(axis=1)  # 4쌍의 좌표 각각 x+y 계산
    diff = np.diff(pts, axis=1)  # 4쌍의 좌표 각각 x-y 계산

    topLeft = pts[np.argmin(sm)]  # x+y가 가장 값이 좌상단 좌표
    bottomRight = pts[np.argmax(sm)]  # x+y가 가장 큰 값이 우하단 좌표
    topRight = pts[np.argmin(diff)]  # x-y가 가장 작은 것이 우상단 좌표
    bottomLeft = pts[np.argmax(diff)]  # x-y가 가장 큰 값이 좌하단 좌표

    # 변환 전 4개 좌표 
    pts1 = np.float32([topLeft, topRight, bottomRight, bottomLeft])

    # 변환 후 4개 좌표
    pts2 = np.float32([[0, 0], [799, 0],
                               [799, 399], [0, 399]])

    # 변환 행렬 계산 
    mtrx = cv2.getPerspectiveTransform(pts1, pts2)
    # 원근 변환 적용
    #result = cv2.warpPerspective(img, mtrx, (int(width), int(height)))
    result = cv2.warpPerspective(img, mtrx, (800, 400))

    return result

def onMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param.append((x, y))

def drawPoints(img, points):
    for point in points:
        cv2.circle(img, (int(point[0]), int(point[1])), 3, (0,255,0), -1)

def drawLines(img, points):
    for i in range(len(points)-1):
        cv2.line(img, points[i], points[i+1], (255,0,0), 1)
    cv2.line(img, points[-1], points[0], (255,0,0), 1)

def drawChess(img, cp):
    img_h = []
    for i in range(4):
        img_v = []
        for j in range(8):
            img_temp = PerspecTrans(img, (cp[i][j], cp[i+1][j], cp[i+1][j+1], cp[i][j+1]))
            img_v.append(img_temp)
        img_temp2 = cv2.hconcat(img_v)
        img_h.append(img_temp2)
    img_pt = cv2.vconcat(img_h)

    return img_pt

def getPoints(im0, points):
    win_name = "Points"
    cv2.namedWindow(win_name)

    cv2.setMouseCallback(win_name, onMouse, param = points)
    key = 0
    while key != 113:
        img = im0.copy()
        drawPoints(img, points)
        cv2.imshow(win_name, img)
        key = cv2.waitKey(10)
    cv2.destroyAllWindows()

def getCross(p1, p2, p3, p4):
    x = ((p1[0]*p2[1] - p1[1]*p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0]-p2[0])*(p3[1]-p4[1]) - (p1[1]-p2[1])*(p3[0]-p4[0]))
    y = ((p1[0]*p2[1] - p1[1]*p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0]-p2[0])*(p3[1]-p4[1]) - (p1[1]-p2[1])*(p3[0]-p4[0]))
    return (int(x), int(y))

def CrossPoints(img, points):
    up = []
    dp = []
    lp = []
    rp = []

    for i, point in enumerate(points):
        if i < 9:
            up.append(point)
        elif i < 18:
            dp.append(point)
        elif i < 23:
            lp.append(point)
        else:
            rp.append(point)
    cp = []

    for p3, p4 in zip(lp, rp):
        cross = []
        for p1, p2 in zip(up, dp):
            cross.append(getCross(p1, p2, p3, p4))
        cp.append(cross)
    
    for cross in cp:
        for point in cross:
            cv2.circle(img, point, 3, (0,255,0), -1)

    return cp

def drawSquare(img, cp):
    for i in range(4):
        for j in range(8):
            drawLines(img, (cp[i][j], cp[i+1][j], cp[i+1][j+1], cp[i][j+1]))

# def main():
#     video_path = 'q_shot1.mp4'
#     cap = cv2.VideoCapture(video_path)
    
#     points = []

#     ret, img = cap.read()

#     getPoints(img, points)

#     cp = CrossPoints(img, points)
#     while(cap.isOpened()):
#         drawSquare(img, cp)
#         img2 = drawChess(img, cp)
#         cv2.imshow("Original", img)

#         cv2.imshow('temp', img2)
#         cv2.waitKey(int(1000/30))
#         ret, img = cap.read()
#     cv2.waitKey(0)

# main()