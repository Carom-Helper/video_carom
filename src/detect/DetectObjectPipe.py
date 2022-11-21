import torch
import argparse
import time

# set path
import sys
from pathlib import Path
import os


CAROM_BASE_DIR = Path(__file__).resolve()
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0].__str__()

# tmp = ROOT
# if str(tmp) not in sys.path and os.path.isabs(tmp):
#     sys.path.append(str(tmp))  # add ROOT to PATH
# tmp = ROOT + '/weights'
# if str(tmp) not in sys.path and os.path.isabs(tmp):
#    WEIGHT_DIR= (str(tmp))  # add Weights ROOT to PATH


# Set weight directory
WEIGHT_DIR = None
temp = ROOT / 'weights'

if str(tmp) not in sys.path and os.path.isabs(tmp):
    WEIGHT_DIR = (tmp)  # add yolov5 ROOT to PATH
    
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


# import my project
# from Singleton import Singleton
from pipe_cls import One2OnePipe, ResourceBag
from IWeight import IWeight
from npu_weight import NPUDetectObjectWeight
from gpu_weight import GPUDetectObjectWeight
from cpu_weight import CPUDetectObjectWeight
from detect_utils import (PipeResource, LoadImages, copy_piperesource, is_test, cv2, print_args)

from CheckDetectPipe import *

def is_test_detect_object()->bool:
    return True and is_test()

def test_print(s, s1="", s2="", s3="", s4="", s5="", end="\n"):
    if is_test():
        print("detect object pipe test : ", s, s1, s2, s3, s4, s5, end=end)

###################################
from threading import Lock

class DetectObjectPipe(One2OnePipe):
    cls_list = ["EDGE", "BALL"]
    def __init__(
        self,
        framework="cpu",
        imgsz=(640,640),
        device,
        ):
        # 고정값
        WEIGHTS = WEIGHT_DIR + "/yolo_ball.pt"
        self.yolo_weights = WEIGHTS
        self.device = select_device(device)
        
        # 변하는 값(입력 값)
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.max_det = max_det
        # classes = None  # filter by class: --class 0, or --class 0 2 3
        self.cls = cls
        self.imgsz = imgsz  # inference size (height, width)
        
        ### load model ###
        instance = NPUDetectObjectWeight(device=device) if device=="furiosa" or device=='onnx' else GPUDetectObjectWeight(device=device)
        self.model = instance
        self.lock = instance.lock
        self.framework = device
        
        t2 = time.time()
        if display:
            print(f'[{str(framework).upper()} YOLOv5 init {(t2-t1):.1f}s]')
            

    @torch.no_grad()
    def exe(self, input: PipeResource) -> PipeResource:
        t1 = time.time()
        output = PipeResource()

        # 고정 값
        visualize = False
        agnostic_nms = False
        classes = None
        device = 'cpu'
       
        # 고정 값
        model = self.model
        dt = [0.0, 0.0, 0.0, 0.0]

        # preprocess
        t1 = time.time()
        im = model.preprocess(input.im)
        t2 = time.time()
        dt[0] += t2 - t1

        # Inference
        with self.lock:
            pred = model.inference(im, input.im.shape)
        t3 = time.time()
        dt[1] += t3 - t2

        # Process detections
        for det in pred:  # detections per image
            test_print(det)
            for xmin, ymin, xmax, ymax, conf, cls in det: #detect datas
                output_det = {
                    "xmin": int(xmin),
                    "ymin": int(ymin),
                    "xmax": int(xmax),
                    "ymax": int(ymax),
                    "conf": int(conf),
                    "cls: : int(cls),
                    "label": self.cls_list[int(cls)]
                }
                input.dets.append(output_det)
            output = copy_piperesource(input)
            
            t2 = time.time()
            if self.display:
                detect_len = output.len_detkey_match("cls", "1")
                detect_len = "" if detect_len == 3 else f"(det ball :{str(detect_len)})"
                print(f'[{detect_len}YOLOv5 run {t2-t1:.3f}s {str(self.framework).upper()}]')
                
            output.print(on=(is_test_detect_object()))
            if is_test_detect_object():
                print(f'[{str(self.framework).upper()} YOLOv5 run {t2-t1:3.f}s]')
            return output
       
    def get_regist_type(self, idx=0) -> str:
        return "det_obj"
    
def test(src, device, display=True):

            p, im0, _ = input.path, input.im0s.copy(), getattr(input, 'frame', 0)
            p = Path(p)

            ## 추가 ##
            annotator = Annotator(
                im0, line_width=3, example=str(self.model.names))
            if len(det):
                det[:, :4] = scale_coords(
                    im.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)
                    label = None
                    annotator.box_label(xyxy, label, color=colors(c, True))

            #### 좌표 변환 ####
            cxywh = xyxy2xywh(det[:, 0:4])

            #### 바운딩 박스 & center x,y 점 ####
            im0 = annotator.result()
            for i in range(det.shape[0]):
                cv2.circle(im0, (int(cxywh[i][0]), int(
                    cxywh[i][1])), 4, (0, 255, 0), -1)

            ## output 설정 ###
            for i in range(det.shape[0]):
                output_det = {"frame": input.f_num, "x": int(det[i][0]), "y": int(det[i][1]), "w": int(
                    det[i][2]), "h": int(det[i][3]), "conf": float(det[i][4]), "cls": int(det[i][5])}
                input.dets.append(output_det)

        output = copy_piperesource(input)
        t2 = time.time()
        ball_det_len = output.len_detkey_match("cls", "1")
        ball_det_len = "" if ball_det_len == 3 else f"(det ball :{str(ball_det_len)})"
        if self.display:
            print(f'[{ball_det_len}YOLOv5 run {t2-t1:.3f}s]', end=" ")
        
        output.print(on=(is_test() and output.__len__() < 7))
        return output

    def get_regist_type(self, idx=0) -> str:
        return "det_obj"


    @torch.no_grad()
    def runascapp(self, input: PipeResource):
        t1 = time.time()
        output = PipeResource()

        # 고정 값
        device = self.device
        model = self.model
        dt = [0.0, 0.0, 0.0, 0.0]

        
        # preprocess
        t1 = time.time()
        im = model.preprocess(input.im)
        
        ## 수정중인 부분
        im = im.float()  # im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        pred = model(im, augment=False, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # Apply NMS
        pred = non_max_suppression(
            pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            seen += 1

            p, im0, _ = input.path, input.im0s.copy(), getattr(input, 'frame', 0)
            p = Path(p)

            ## 추가 ##
            annotator = Annotator(
                im0, line_width=3, example=str(self.model.names))
            if len(det):
                det[:, :4] = scale_coords(
                    im.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    c = int(cls)
                    label = None
                    annotator.box_label(xyxy, label, color=colors(c, True))

            #### 좌표 변환 ####
            cxywh = xyxy2xywh(det[:, 0:4])

            #### 바운딩 박스 & center x,y 점 ####
            im0 = annotator.result()
            for i in range(det.shape[0]):
                cv2.circle(im0, (int(cxywh[i][0]), int(
                    cxywh[i][1])), 4, (0, 255, 0), -1)

            ## output 설정 ###
            for i in range(det.shape[0]):
                output_det = {"frame": input.f_num, "x": int(det[i][0]), "y": int(det[i][1]), "w": int(
                    det[i][2]), "h": int(det[i][3]), "conf": float(det[i][4]), "cls": int(det[i][5])}
                input.dets.append(output_det)
                #print(f'{i}-{output_det}')
                output.append(output_det)
        
        t2 = time.time()
        
        if self.display:
            print(f'[{len(output)} YOLOv5 run {t2-t1:.3f}s]', end=" ")
        
        return output

    def get_regist_type(self, idx=0) -> str:
        return "det_obj"

def test(src, device, display=True):
    ### Pipe 생성 & 연결 ###
    detectObjectPipe1 = DetectObjectPipe(device=device, display=display)
    bag_split = ResourceBag()
    
    detectObjectPipe1.connect_pipe(bag_split)

      
    
    ### SplitCls 생성 & 연결 ###
    bag_split = ResourceBag()
    split_cls.connect_pipe(find_edge_pipe)
    split_cls.connect_pipe(check_detect_pipe)
    check_detect_pipe.connect_pipe(bag_split)
    
    ### Dataloader ###
    source = src
    imgsz = (640, 640)

    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    
    ### 실행 ###
    for frame_idx, (path, im, im0s, vid_cap, s) in enumerate(dataset):
        input = PipeResource(f_num=frame_idx, path=path,
                             im=im, im0s=im0s, vid_cap=vid_cap, s=s)
        detectObjectPipe1.push_src(input)
    
    bag_split.print_all()

def runascapp(src, device):
    ### Pipe 생성 & 연결 ###
    detectObjectPipe1 = DetectObjectPipe(device=device)
    split_cls = SplitCls()
    find_edge_pipe = FindEdgePipe()
    check_detect_pipe = CheckDetectPipe()
    detectObjectPipe1.connect_pipe(split_cls)

    ### SplitCls 생성 & 연결 ###
    bag_split = ResourceBag()
    split_cls.connect_pipe(find_edge_pipe)
    split_cls.connect_pipe(check_detect_pipe)
    check_detect_pipe.connect_pipe(bag_split)
    
    ### Dataloader ###
    source = src
    imgsz = (640, 640)
    pt = True
    stride = 32
    nr_sources = 1

    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
    vid_path, vid_writer, txt_path = [
        None] * nr_sources, [None] * nr_sources, [None] * nr_sources

    ### 실행 ###
    for im0, path, s in dataset:
        metadata = {"path": path}
        images = {"origin":im0}
        input = PipeResource(im=im0, metadata=metadata, images=images, s=s)
        detectObjectPipe1.push_src(input)
    
    if display:
        for src in bag_split.src_list:
            src.imshow(name="hellow")
            cv2.waitKey(1000)
    else:
        bag_split.print()
  
        
def test_singleton():
    gpu = DetectObjectPipe(device="cpu")
    #cpu = DetectObjectPipe(device="0")
    
    print(id(gpu.model))
    #print(id(cpu.model))

def runner(args):
    #test(args.src, args.device)
    runascapp(args.src, args.device)
    #test_singleton()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', default=(CAROM_BASE_DIR / "media" / "test2"))
    parser.add_argument('--device', default='cpu', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--no_display', default=True, action="store_false")
    args = parser.parse_args()
    runner(args) 

  
