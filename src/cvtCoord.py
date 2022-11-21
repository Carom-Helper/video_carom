import numpy as np
import cv2

class coord:
    def setData(self, x, y):
        self.x = x
        self.y = y


def make_pers(csh_line):
    # 네 점
    TLT = coord()
    TLB = coord()
    TRT = coord()
    TRB = coord()

    coord_list = [csh_line[0][0], csh_line[1]
                  [0], csh_line[2][0], csh_line[3][0]]

    # 좌표 정렬
    coord_list.sort(key=lambda x: (x[0], x[1]))

    if coord_list[0][1] < coord_list[1][1]:
        TLT.setData(coord_list[0][0], coord_list[0][1])
        TLB.setData(coord_list[1][0], coord_list[1][1])
    else:
        TLT.setData(coord_list[1][0], coord_list[1][1])
        TLB.setData(coord_list[0][0], coord_list[0][1])
    if coord_list[2][1] < coord_list[3][1]:
        TRT.setData(coord_list[2][0], coord_list[2][1])
        TRB.setData(coord_list[3][0], coord_list[3][1])
    else:
        TRT.setData(coord_list[3][0], coord_list[3][1])
        TRB.setData(coord_list[2][0], coord_list[2][1])

    # 좌표 변환
    srcQuad = np.array([[TLT.x, TLT.y], [TLB.x, TLB.y], [
        TRT.x, TRT.y], [TRB.x, TRB.y]], np.float32)
    dstQuad = np.array([[0, 0], [0, 399], [799, 0], [799, 399]], np.float32)
    pers = cv2.getPerspectiveTransform(srcQuad, dstQuad)

    return pers

def cvtCoord(x,y, pers):
  src = np.array([[[x, y]]], dtype='float32')
  dst = cv2.perspectiveTransform(src, pers)
  return dst[0][0][0], dst[0][0][1]
  
def cvtball(ball, pers):
    for b in ball.modified_ball_list:
        b.x, b.y = cvtCoord(b.x, b.y, pers)

def cvtline(line, pers):
    new_line = []
    for l in line:
        x, y = cvtCoord(l[0], l[1], pers)
        new_line.append((x,y))

    return new_line

def cvtimgs(imgs, pers):
    new_imgs = []
    for img in imgs:
        img = cv2.warpPerspective(img, pers, (800, 400))
        new_imgs.append(img)
    return new_imgs

def cvtcsh(cshList, pers):
    new_cshList = []
    for csh in cshList:
        x, y = cvtCoord(csh[0], csh[1], pers)
        new_cshList.append((x,y))
    return new_cshList