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
ROOT = FILE.parent

temp = ROOT

tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
ROOT = ROOT / 'detect'  # yolov5 strongsort root directory
tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
ROOT = ROOT / 'yolo_sort'  # yolov5 strongsort root directory
tmp = ROOT
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add ROOT to PATH
tmp = ROOT / 'yolov5'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add yolov5 ROOT to PATH
tmp = ROOT / 'strong_sort'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add strong_sort ROOT to PATH
tmp = ROOT / 'strong_sort/deep/reid'
if str(tmp) not in sys.path and os.path.isabs(tmp):
    sys.path.append(str(tmp))  # add strong_sort ROOT to PATH
ROOT=temp
test_print(sys.path)

import cv2
import numpy as np
import math
import time
import threading
from pickle import NONE

from pipe_factory import pipe_factory
from Detect_utils import LoadImages, PipeResource
from DetectError import NotEnoughDetectError
from ballpredictor import ballPredictor
from main_utils import check_unique_directory, create_directory


def run(src, dst, device='cpu', vnum="", display=False):
    print(f'======== [ {src} ] ========' )
    print("main start ... ")
    t1 = time.time()
    
    # set dataloader
    nr_sources = 1
    imgsz = (640, 640)
    pt = True
    stride = 32
    
    dataset = LoadImages(src)
    # set pipe
    pipe, ball_bags, edge_bag = pipe_factory(device=device, display = display)
    notdetect_error = False
    # run detect
    for frame_idx, (im0, path, s) in enumerate(dataset):
        metadata = {"f_num": frame_idx, "path":path}
        images = {"origin":im0}
        input = PipeResource(im=im0, metadata=metadata, images=images, s=s)
        if display:
            print(f"{vnum}| Detect [{frame_idx}] frame:",end=" ")
        try:
            pipe.push_src(input)
        except NotEnoughDetectError as e:
            print()
            print(str(e))
            notdetect_error= True
            break

        if display:
            print("")
    
    # #test yolo reader
    
    # from DetectIndexPipe import yolofile_reader
    # from pipe_factory import detected_pipe_factory
    # dataset = yolofile_reader(src)
    # pipe, ball_bags, edge_bag = detected_pipe_factory(device=device)
    # for frame_idx, input in enumerate(dataset):
    #     if frame_idx == 0:
    #         test_print(input.im0s.shape, input.im0s.shape[1])
    #         video_shape = input.im0s.shape
    #     # if is_test():
    #     #     cv2.imshow("hello", input.im0s)
    #     #     cv2.waitKey(1)
    #     img_list.append(input.im0s)
    #     print(f"{vnum}| Detect [{frame_idx}] frame:",end=" ")
    #     pipe.push_src(input)
    #     print()
    
    # cut index ##################### 나중에 파이프로 넣기 #######################
    ball_bag_list = []
    MIN_DETS = 10
    for i, bag in enumerate(ball_bags):
        cnt = 0
        test_print("bag idx", i, "bag num", bag.__len__())
        for resource in bag.src_list:
            # counting det num
            if resource.__len__() > 0 :
                #resource.print()
                cnt += 1
                #test_print(f"cnt({cnt})")
        if cnt > MIN_DETS : 
            test_print(f"{i} bag cnt({cnt})")
            test_print("bag type : ", type(bag))
            ball_bag_list.append(bag.get_list())
            
    edge_bag = edge_bag.get_edge()
    t2 = time.time()
    print(f'detect ... {t2-t1} sec elapsed')
    #edges.make_list()
    test_print("ball bags len : ", ball_bag_list.__len__())
    
    if is_test():
        title = "test"
        for bag in ball_bags:
            for ball_det in bag.src_list:
                ball_det.imshow(title, idx_names=["1","2","3","4","5","6"], hide_labels=False)
                cv2.waitKey(20)
    
    print("==============================predict start============================")
    eventstr, draw_imgs = ballPredictor(ball_bag_list, edge_bag, video_shape[1], img_list)
    t3 = time.time()
    print(f'predict ... {t3-t2} sec elapsed')
    if display:
        print(eventstr)
    t4 = t3
    print(f'main end ... {t4-t1} sec elapsed')
    
    print("==============================output result============================")
    bfname = os.path.abspath(src)
    bf_basename = os.path.basename(bfname).split(".")[0]
    vidname = f'{dst}/{bf_basename}_track.mp4'
    txtname = f'{dst}/{bf_basename}_out.txt'
    print("origin :", bfname)
    print("video result :", vidname)
    print("txt result :", txtname)
    print(len(draw_imgs))
    
    cap = cv2.VideoCapture(bfname)
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps = 30 if fps == 0 else fps
    print("fps", fps)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(vidname, fourcc, fps, (800, 400))
    for draw_img in draw_imgs:
        out.write(draw_img)
        # if is_test:
        #     cv2.imshow('test', draw_img)
        #     cv2.waitKey(1)
        #print(f"{i}/{len(imgs)-1} vid writing")
    out.release()
    
    txt = open(txtname, 'w')
    txt.write(eventstr)
    txt.close()
    
    


def runner(args):
    dst = check_unique_directory(f"{args.dst}/{args.name}")
    dst = create_directory(dst)
    filelist = []
    print("src :",args.src, " | dst :", dst)
    if os.path.abspath(args.src).split('.')[-1] == "mp4" :
        filelist.append(os.path.abspath(args.src))
    else :
        for (root, _, files) in os.walk(args.src):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.split('.')[-1] == "mp4":
                    filelist.append(os.path.abspath(file_path))
    # print(filelist)

    for i, file in enumerate(filelist):
        run(file, dst, args.device, f"({i+1}/{len(filelist)})", args.display)
    #run(src=args.src, device=args.device)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default= FILE.parent.parent / "test"/"origin_ts_cudlong.mp4")####.mp4
    parser.add_argument('--device', default='furiosa', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--dst', default=ROOT / "runs")
    parser.add_argument('--name', default="output")
    parser.add_argument('--display', action="store_true")

    args = parser.parse_args()
    print(args)
    runner(args)    
