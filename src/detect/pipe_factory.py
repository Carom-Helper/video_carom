import torch
import numpy as np
import argparse

# set path
import os
from pathlib import Path
import sys

CAROM_BASE_DIR=Path(__file__).resolve().parent
FILE = Path(__file__).resolve()
ROOT = FILE.parent

tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
     sys.path.append(str(tmp))  # add ROOT to PATH

tmp = ROOT / "npu_yolov5"
# tmp = ROOT / "cpu_yolov5"
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add yolov5 ROOT to PATH
    
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from pipe_cls import One2OnePipe, ConvertToxywhPipe, IObserverPipe, ResourceBag, SplitCls, ResourceBag
from Singleton import Singleton
from projectionPipe import ProjectionCoordPipe
from DetectObjectPipe import DetectObjectPipe #NPU_YOLO_DIR, CPU_YOLO_DIR
from detect_utils import (PipeResource, LoadImages, is_test, cv2, print_args)

def is_test_factory()->bool:
     return False and is_test()

def test_print(s, s1="", s2="", s3="", s4="", s5="", end="\n"):
     if is_test_factory():
          print("factory pipe test : ", s, s1, s2, s3, s4, s5, end=end)
          
def PipeFactory(metaclass=Singleton):
     def __init__(self, start_pipe=None, device='cpu', display=True, inDB=True):
          self.pipe, _ = pipe_factory(start_pipe=start_pipe, device=device, display=display, inDB=inDB)

def pipe_factory(start_pipe=None, device='cpu', display = True, inDB=True):
    if display:
        print("initialize weights")
    #detect class and split class
    detect_cls_pipe = DetectObjectPipe(device=device, display=display)
    xyxy2xywh = ConvertToxywhPipe()
    split_cls_pipe = SplitCls()
    edge_bag = ResourceBag()
    projection_coord_pipe = ProjectionCoordPipe(display=display)
 
    
    # - connect
    detect_cls_pipe.connect_pipe(split_cls_pipe)     #detect class - split_cls
    xyxy2xywh.connect_pipe(projection_coord_pipe)    #detect class - split_cls
    projection_coord_pipe.connect_pipe(split_cls_pipe)
    _ = split_cls_pipe.connect_pipe(edge_pipe) # split class - edge bag
    
     
    test_print("connect edge pipe : ", _)        
    
    
    #detect index and split index
    detect_idx_pipe = DetectIndexPipe(device=device, display=display)
    xywh_pipe = ConvertToxywhPipe()
    repeat_pipe = FirstCopyPipe(N_INIT=detect_idx_pipe.N_INIT, display=display)
    force_setid_pipe = ForceSetIdPipe(display=display)
    check_detect_pipe = CheckDetectPipe()
    start_cutter_pipe = StartNotDetectCutterPipe()
    
    
    #connect
    detect_cls_pipe.connect_pipe(xyxy2xywh)
    xyxy2xywh.connect_pipe(projection_coord_pipe)
    projection_coord_pipe.connect_pipe(split_cls_pipe)
    _ = split_cls_pipe.connect_pipe(edge_bag)

    test_print("connect edge pipe : ", _)
     
    ball_bag = SaveBallCoordPipe(display=display) id inDB else ResourceOne()
    _ = split_cls_pie.connect_pipe(ball_bag)
    test_print("connect ball pipe : ", _)

    
    #set start_pipe end_pipe
    if start_pipe is None:
        start_pipe = detect_cls_pipe
    elif isinstance(start_pipe, IObserverPipe):
        start_pipe.connect_pipe(detect_cls_pipe)
    else:
        raise TypeError("TypeError in pipe_factory")
    return start_pipe, ball_bag


def detect(src, device='cpu', MIN_DETS= 10, display=False, inDB=False):
    # # set pipe
    pipe, ball_bag = pipe_factory(device=device, display=display, inDB=inDB)
    
    ### Dataloader ###
    dataset = LoadImages(src)
    ### 실행 ###
    for im0, path, s in dataset:
        #point 위치 확인
        points = [[549,109],[942,111],[1270,580],[180,565]]
        pts = np.zeros((4, 2), dtype=np.float32)
        for i in range(4):
            pts[i] = points[i]
        
        sm = pts.sum(axis=1)  # 4쌍의 좌표 각각 x+y 계산
        diff = np.diff(pts, axis=1)  # 4쌍의 좌표 각각 x-y 계산

        topLeft = pts[np.argmin(sm)]  # x+y가 가장 값이 좌상단 좌표
        bottomRight = pts[np.argmax(sm)]  # x+y가 가장 큰 값이 우하단 좌표
        topRight = pts[np.argmin(diff)]  # x-y가 가장 작은 것이 우상단 좌표
        bottomLeft = pts[np.argmax(diff)]  # x-y가 가장 큰 값이 좌하단 좌표
        test_print(f'topLeft({type(topLeft)}):{topLeft} | ({type(bottomRight)}):{bottomRight} | ({type(topRight)}):{topRight} | ({type(bottomLeft)}):{bottomLeft}')
        

        metadata = {"path": path, "carom_id":1, "TL":topLeft, "BR":bottomRight, "TR":topRight, "BL":bottomLeft}
        images = {"origin":im0}
        input = PipeResource(im=im0, metadata=metadata, images=images, s=s)
        pipe.push_src(input)
        # 원본 정사영 영역 표시
        if display:
            origin = input.images["origin"].copy()
            for i in range(4):
                origin = cv2.line(origin, (pts[i][0], pts[i][1]), (pts[(i+1)%4][0], pts[(i+1)%4][1]), (0, 255, 0), 2)
            cv2.imshow("origin", origin)
            cv2.waitKey(3000)
    return ball_bag
    
def test(src = CAROM_BASE_DIR / "data", 
         device = '0'
         display = True):
         ball_bag = detect(src, device, display=display)
     
         title = "test"
         ball_bag.print()
     
     
def runner(args):
    print_args(vars(args))
    test(args.src, args.device)
    #run(args.src, args.device)
    #detect(args.src, args.device)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default="/../../data/videos/kj_cud_272.mp4")
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--display', action='store_true')
    args = parser.parse_args()
    print(args.src)
    runner(args) 
