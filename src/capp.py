def is_test()->bool:
    return False

def test_print(s, s1="", s2="", s3="", s4="", s5=""):
    if is_test():
        print("main test : ", s, s1, s2, s3, s4, s5)

import argparse
import os
from pathlib import Path
import sys


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0].__str__()

temp = ROOT

tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
ROOT = ROOT + '/detect'  # yolov5 strongsort root directory
tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
ROOT = ROOT + '/yolo_sort'  # yolov5 strongsort root directory
tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
tmp = ROOT + '/yolov5'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add yolov5 ROOT to PATH
tmp = ROOT + '/strong_sort'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add strong_sort ROOT to PATH
tmp = ROOT + '/strong_sort/deep/reid'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add strong_sort ROOT to PATH
ROOT=temp
test_print(sys.path)

import cv2
import numpy as np
import random


from pipe_factory import *
from DetectError import NotEnoughDetectError
from ballpredictor import ballPredictor
from main_utils import check_unique_directory, create_directory
from DetectObjectPipe import runascapp


# retrun DetectObjectPipe.py
def getPoint():
    rdn = random.randrange(1,10)
    ptlistnormal = [ {'frame': 0, 'x': 302, 'y': 767, 'w': 351, 'h': 818, 'conf': 0.9270716905593872, 'cls': 0},
            {'frame': 0, 'x': 1576, 'y': 766, 'w': 1624, 'h': 817, 'conf': 0.9208700060844421, 'cls': 0},
            {'frame': 0, 'x': 1575, 'y': 107, 'w': 1624, 'h': 158, 'conf': 0.9203038215637207, 'cls': 0},
            {'frame': 0, 'x': 303, 'y': 108, 'w': 351, 'h': 159, 'conf': 0.9142023324966431, 'cls': 0},
            {'frame': 0, 'x': 949, 'y': 370, 'w': 978, 'h': 402, 'conf': 0.8789270520210266, 'cls': 1},
            {'frame': 0, 'x': 608, 'y': 471, 'w': 636, 'h': 501, 'conf': 0.8699398040771484, 'cls': 1},
            {'frame': 0, 'x': 644, 'y': 371, 'w': 671, 'h': 401, 'conf': 0.8519392013549805, 'cls': 1} ]


    ptlist3_1 = [ {'frame': 0, 'x': 302, 'y': 767, 'w': 351, 'h': 818, 'conf': 0.9270716905593872, 'cls': 0},
            {'frame': 0, 'x': 1576, 'y': 766, 'w': 1624, 'h': 817, 'conf': 0.9208700060844421, 'cls': 0},
            {'frame': 0, 'x': 1575, 'y': 107, 'w': 1624, 'h': 158, 'conf': 0.9203038215637207, 'cls': 0},
            {'frame': 0, 'x': 949, 'y': 370, 'w': 978, 'h': 402, 'conf': 0.8789270520210266, 'cls': 1},
            {'frame': 0, 'x': 608, 'y': 471, 'w': 636, 'h': 501, 'conf': 0.8699398040771484, 'cls': 1},
            {'frame': 0, 'x': 644, 'y': 371, 'w': 671, 'h': 401, 'conf': 0.8519392013549805, 'cls': 1} ]

    if (rdn % 2) == 0:
        return ptlist3_1
    else:
        return ptlistnormal


def drawCircle(img_draw, x, y, radius, colortype='w'):   
    if colortype == 'w':
        drawcolor = ([250, 250, 250])        
    elif colortype == 'r':
        drawcolor = ([0, 0, 250])        
    elif colortype == 'y':
        drawcolor = ([20, 210, 230])
    else:
        drawcolor = ([250, 0, 5])

    cv2.circle(img_draw, (x, y), radius, drawcolor, 2)


def drawLine(img_draw, x, y, bx, by, lines, color):
    xx = int(x)
    yy = int(y)

    if lines is None:
        lines = np.zeros_like(img_draw)
    else:
        cv2.line(lines, (bx, by), (xx, yy),  color, 2)

    return lines


def getQuad(point):
    if point[0] > 810:
        if point[1] > 400:
            return '4QD'
        else:
            return '1QD'
    else:
        if point[1] > 400:
            return '3QD'
        else:
            return '2QD'


def xyTable(tlist):
    tl = bl = tr = br = None
    for item in tlist:
        strQD = getQuad(item)        
        if strQD == '1QD':
            tr = item
        elif strQD == '2QD':
            tl = item
        elif strQD == '3QD':
            bl = item
        elif strQD == '4QD':
            br = item

    print('before table ')
    print(tl, tr)
    print(bl, br)
    print('---------')

    if tl is None:
        if not( bl is None) and not (tr is None):
            tl = (bl[0], tr[1])
    if bl is None:
        if not( tl is None) and not (br is None):
            bl = (tl[0], br[1])
    if tr is None:
        if not( tl is None) and not (br is None):
            tr = (br[0], tl[1])
    if br is None:
        if not( tr is None) and not (bl is None):
            br = (tr[0], bl[1])

    tl = (bl[0], tr[1])
    bl = (tl[0], br[1])

    tr = (br[0], tl[1])
    br = (tr[0], bl[1])
    print('---- after table -----')
    print(tl, tr)
    print(bl, br)
    print('---------')

    return tl, bl, tr, br

def makeTable(tlist):
    tlist.sort()

    if len(tlist) == 1:
        print(f'can not get table size {len(tlist)}')
        tlist.append(tlist[0])        
        tlist.append(tlist[0])        
        tlist.append(tlist[0])        
    elif len(tlist) == 2:
        print(f'can not get table size {len(tlist)}')
        tlist.append(tlist[0])        
        tlist.append(tlist[0])        
    elif len(tlist) == 3:
        print(f'can not get table size {len(tlist)}')
        tlist.append(tlist[0])        

    return xyTable(tlist)


def xyParse(ptlist):
    balllist = []
    tablelist = []
    for ptitem in ptlist:
        wh = int((ptitem['w'] - ptitem['x']) / 2)
        hh = int((ptitem['h'] - ptitem['y']) / 2)
        item = (ptitem['x'] + wh, ptitem['y']+hh)
        if ptitem['cls'] == 1:
            balllist.append(item)
        else:
            tablelist.append(item)

    return balllist, tablelist
    


def callBapp(cbpt, obj1pt, obj2pt):
    # TBD
    #guide_shot = bapp_interface(cbpt, obj1pt, obj2pt)

    guide_shot = {
        "cnt": 2,
        "shot":[
            {
                "case": 0,
                "cue": [(200, 200), (590, 200), (680, 10), (780, 150), (480, 390), (210, 150), (200, 120)],
                "obj1": [(600, 200), (700, 120)],
                "obj2": [(200, 150), (150, 130)]
            },            
            {
                "case": 1,
                "cue": [(200, 200), (590, 200), (790, 340), (700, 390), (210, 150), (200, 100)],
                "obj1": [(600, 200), (720, 100)],
                "obj2": [(200, 150), (150, 30)]
            },

        ]        
    }

    aballist = []
    bballist = []
    cballist = []

    for idx, item in enumerate(guide_shot['shot']):
        print(f'case {idx}')
        print(item['cue'])
        print(item['obj1'])
        print(item['obj2'])
        aballist.append(item['cue'])
        bballist.append(item['obj1'])
        cballist.append(item['obj2'])

    return aballist, bballist, cballist


def saveresults(src, aball, bball, cball, tl, bl, tr, br, mode='crop', case=0):
    img = cv2.imread(src)

    if mode == 'crop':
        crop_img = img[tl[1]+25:br[1]-25, tl[0]+25:br[0]-25]
        bgimg = cv2.resize(crop_img, (800, 400))

        greenimg = np.zeros_like(bgimg)

        aballinit = aball[0]
        bballinit = bball[0]
        cballinit = cball[0]
        
        drawCircle(bgimg, aballinit[0], aballinit[1], 8, colortype='w')
        drawCircle(bgimg, bballinit[0], bballinit[1], 8, colortype='r')
        drawCircle(bgimg, cballinit[0], cballinit[1], 8, colortype='y')

        drawCircle(greenimg, aballinit[0], aballinit[1], 8, colortype='w')
        drawCircle(greenimg, bballinit[0], bballinit[1], 8, colortype='r')
        drawCircle(greenimg, cballinit[0], cballinit[1], 8, colortype='y')

        bc = 0
        for balls in [aball, bball, cball]:
            sb = eb = None
            for idx, ab in enumerate(balls):
                if idx == 0:
                    sb = ab
                    continue
                else:
                    eb = ab

                if eb is None:
                    break

                if bc == 0:
                    drawcolor = ([250, 250, 250])        
                elif bc == 1:
                    drawcolor = ([0, 0, 250])        
                elif bc == 2:
                    drawcolor = ([20, 210, 230])
                cv2.line(bgimg, (sb[0], sb[1]), (eb[0], eb[1]), drawcolor, 4)
                cv2.line(greenimg, (sb[0], sb[1]), (eb[0], eb[1]), drawcolor, 4)
                sb = ab
            bc = bc + 1

        rdn = random.randrange(1,9000)
        outname = os.path.join(args.dst, f'capp_{case:03}_crop_{rdn}.jpg')
        cv2.imwrite(outname, bgimg)

        outname = os.path.join(args.dst, f'capp_{case:03}_green_{rdn}.jpg')
        cv2.imwrite(outname, greenimg)
    else:
        bgimg = img.copy()

        #draw into input image
        tl = (tl[0]+25, tl[1]+ 25)
        br = (br[0]-25, br[1]- 25)
        tr = (tr[0]-25, tr[1]+ 25)
        bl = (bl[0]+25, bl[1]- 25)
        
        tablew = tr[0]-tl[0]
        tableh = br[1]-tr[1]

        xweight = tablew/800 * 1000
        yweight = tableh/400 * 1000

        aballinit = aball[0]
        bballinit = bball[0]
        cballinit = cball[0]

        newabx = tl[0] + int(aballinit[0] * xweight / 1000)
        newaby = tl[1] + int(aballinit[1] * yweight / 1000)

        newbbx = tl[0] + int(bballinit[0] * xweight / 1000)
        newbby = tl[1] + int(bballinit[1] * yweight / 1000)

        newcbx = tl[0] + int(cballinit[0] * xweight / 1000)
        newcby = tl[1] + int(cballinit[1] * yweight / 1000)


        # +/- 8 size, 
        drawCircle(bgimg, newabx, newaby, 8, colortype='w')
        drawCircle(bgimg, newbbx, newbby, 8, colortype='r')
        drawCircle(bgimg, newcbx, newcby, 8, colortype='y')

        bc = 0
        for balls in [aball, bball, cball]:
            sb = eb = None
            for idx, ab in enumerate(balls):
                if idx == 0:
                    sb = ab
                    continue
                else:
                    eb = ab

                if eb is None:
                    break
                
                sx = tl[0] + int(sb[0] * xweight / 1000)
                sy = tl[1] + int(sb[1] * yweight / 1000)
                ex = tl[0] + int(eb[0] * xweight / 1000)
                ey = tl[1] + int(eb[1] * yweight / 1000)
                if bc == 0:
                    drawcolor = ([250, 250, 250])        
                elif bc == 1:
                    drawcolor = ([0, 0, 250])        
                elif bc == 2:
                    drawcolor = ([20, 210, 230])
                cv2.line(bgimg, (sx, sy), (ex, ey), drawcolor, 4)
                sb = ab
            bc = bc + 1

        rdn = random.randrange(1,9000)
        outname = os.path.join(args.dst, f'capp_{case:03}_org_{rdn}.jpg')
        cv2.imwrite(outname, bgimg)


def xyConvert(aball, bball, cball, tl, bl, tr, br, mode='DOWN'):
    print(f'{aball}, {bball}, {cball}, {tl, bl, tr, br}, {mode}')
    

    tl = (tl[0]+25, tl[1]+ 25)
    br = (br[0]-25, br[1]- 25)
    tr = (tr[0]-25, tr[1]+ 25)
    bl = (bl[0]+25, bl[1]- 25)
    
    tablew = tr[0]-tl[0]
    tableh = br[1]-tr[1]

    if mode == 'UP':
        xweight = tablew / 800 * 1000
        yweight = tableh / 400 * 1000

        a, b = aball[0]
        newabx = tl[0] + int(a * xweight / 1000)
        newaby = tl[1] + int(b * yweight / 1000)

        a, b = bball[0]
        newbbx = tl[0] + int(a * xweight / 1000)
        newbby = tl[1] + int(b * yweight / 1000)

        a, b = cball[0]
        newcbx = tl[0] + int(a * xweight / 1000)
        newcby = tl[1] + int(b * yweight / 1000)
    else:
        xweight = 800/tablew * 1000
        yweight = 400/tableh * 1000

        newabx = int((aball[0] - tl[0]) * xweight / 1000)
        newaby = int((aball[1] - tl[1]) * yweight / 1000)

        newbbx = int((bball[0] - tl[0]) * xweight / 1000)
        newbby = int((bball[1] - tl[1]) * yweight / 1000)

        newcbx = int((cball[0] - tl[0]) * xweight / 1000)
        newcby = int((cball[1] - tl[1]) * yweight / 1000)
    
    print(f'after {newabx, newaby}, {newbbx, newbby}, {newcbx, newcby}')
    return (newabx, newaby), (newbbx, newbby), (newcbx, newcby)


def gocapp(src, dst, device):
    inpoint = runascapp(src, device)

    balllist, tablelist = xyParse(inpoint)
    tl, bl, tr, br = makeTable(tablelist)

    # convert 800x400
    raball, rbball, rcball = xyConvert(balllist[0], balllist[1], balllist[2], tl, bl, tr, br)
    aballist, bballist, cballist = callBapp(raball, rbball, rcball)

    if aballist is None or len(aballist) == 0:
        print(f'can not found results.')
        return

    for idx, (aball, bball, cball) in enumerate(zip(aballist, bballist, cballist)):
        # convert up
        raball, rbball, rcball = xyConvert(aball, bball, cball, tl, bl, tr, br, mode='UP')

        saveresults(src, aball, bball, cball, tl, bl, tr, br, mode='crop', case=idx)
        saveresults(src, aball, bball, cball, tl, bl, tr, br, mode='original', case=idx)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="./1231.jpg")
    parser.add_argument('--dst', default="./todel/")
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')

    os.makedirs('./todel', exist_ok=True)
    args = parser.parse_args()
    gocapp(args.src, args.dst, args.device)