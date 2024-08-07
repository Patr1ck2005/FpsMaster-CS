import time
import numpy as np
import torch
from torchvision.ops import nms
# from cs_master.controller import BaseController  # strange
from models.common import DetectMultiBackend
from ultralytics.utils.plotting import Annotator
from ultralytics.utils.plotting import colors
from utils.general import (cv2, non_max_suppression)
from cs_master.settings import *


class Detector:
    def __init__(self):
        self.pred_rebuild_pixel_pos = None
        self.mouse_rebuild = None
        self.pred_pixel_r_pos = None
        self.im0 = None
        self.lost_target_before = True
        self.target_pos_r = (None, None)
        self.marker_x_lst = []
        self.target_xx = (None, None)
        self.head_size = (None, None)
        # self.device = select_device(device)
        self.device = torch.device('cuda:0')
        self.model = DetectMultiBackend(weights_path, device=self.device, dnn=False, data=data_path, fp16=True)
        self.names = self.model.names
        self.detect_region_pos = (WINDOW_SIZE[0] / 2 - SHOT_SIZE[0] / 2, WINDOW_SIZE[1] / 2 - SHOT_SIZE[1] / 2)
        self.mouse_x = WINDOW_SIZE[0] / 2
        self.mouse_y = WINDOW_SIZE[0] / 2
        self.n_target = 0
        self.old_xyxy = None
        self.mode = None
        self.CONF_THRES = 0.3
        self.HEAD_CONF_THRES = 0.7
        self.IMG_VIEW = False
        self.head_track = True
        self.body_track = False

    def reset_model(self, path):
        self.model = DetectMultiBackend(path, device=self.device, dnn=False, data=data_path, fp16=True)
        self.names = self.model.names

    @staticmethod
    def timeit(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            func(*args, **kwargs)
            end = time.time()
            print(f'function {func.__name__} cost {end - start}s')
        return wrapper

    def detect(self, image):
        # t1 = time.time()
        self.im0 = np.ascontiguousarray(np.array(image))
        im = image.transpose((2, 0, 1))  # HWC to CHW
        im = np.ascontiguousarray(im)
        im = torch.from_numpy(im).to(self.model.device)
        im = im.half() if self.model.fp16 else im.float()  # uint8 to fp16/32
        im /= 255
        if len(im.shape) == 3:
            im = im[None]
        # t2 = time.time()
        # test: img pre-process about 1000 fps
        # print(f'img pre-process {1/(t2-t1+0.0000001)}'.center(100))
        pred = self.model(im, augment=False, visualize=visualize)
        pred = non_max_suppression(pred, self.CONF_THRES, iou_thres, classes, agnostic_nms, max_det=max_det)  # 极大值抑制
        self.n_target = pred[0].shape[0]
        # t3 = time.time()
        # test: yolov5 about 80 fps
        # print(f'yolov5 {1/(t3-t2)}'.center(100))
        return pred

    def find_target(self, prediction):
        for det in prediction:
            annotator = Annotator(self.im0, line_width=line_thickness, example=str(self.names))
            _offset = 999999999.0
            _marker_offset = 999999999.0
            _iou = 0
            _rect_xyxy: list
            _class: float
            # first = True
            self.target_pos_r = (None, None)
            self.marker_x_lst = []
            self.target_xx = (None, None)
            # if not det.any():     # no target
            #     self.lost_target_before = True
            #     self.old_xyxy = None
            for *_rect_xyxy, _confidence, _class in det:
                mid_x = (_rect_xyxy[0] + _rect_xyxy[2]) / 2
                if _class == 3:
                    self.marker_x_lst.append(mid_x)
            for *_rect_xyxy, _confidence, _class in det:
                mid_x = (_rect_xyxy[0] + _rect_xyxy[2]) / 2
                mid_y = (_rect_xyxy[1] + _rect_xyxy[3]) / 2
                body_y = (0.75*_rect_xyxy[1] + 0.25*_rect_xyxy[3])
                target_size = (_rect_xyxy[2] - _rect_xyxy[0], _rect_xyxy[3] - _rect_xyxy[1])
                target_pos = (mid_x, mid_y)
                if self.IMG_VIEW:
                    c = int(_class)
                    label = None if hide_labels else (self.names[c] if hide_conf else f'{self.names[c]}{_confidence:.2f}')
                    annotator.box_label(_rect_xyxy, label, color=colors(c, True))
                # if self.lost_target_before:
                #     if target_pos[0] <= shot_size[0] / 2:
                #         self.mode = 'left'
                #     else:
                #         self.mode = 'right'
                # if self.lost_target_before:
                #     self.old_xyxy = _rect_xyxy
                if self.head_track and _class == 1 and _confidence > self.HEAD_CONF_THRES:
                    if target_size[1] / SHOT_SIZE[1] > 0.5:
                        continue
                    team = False
                    for marker_x in self.marker_x_lst:
                        if mid_x-target_size[0]*1.5 < marker_x < mid_x+target_size[0]*1.5:
                            team = True
                            break
                    if team:
                        continue
                    target_offset = self.cal_offset(target_pos)
                    # target_iou = self.box_iou_xyxy(rect_xyxy, self.old_xyxy, 5)
                    if target_offset < _offset:
                        _offset = target_offset
                        self.target_pos_r = (mid_x, mid_y)
                        self.target_xx = _rect_xyxy[0], _rect_xyxy[2]
                        self.head_size = target_size
                    # print(target_iou, 'and', _iou)
                    # if target_iou >= _iou:
                    #     _iou = target_iou
                    #     self.old_xyxy = rect_xyxy
                    #     self.target_pos_r = (mid_x, mid_y)
                    #     self.head_size = target_size

                    # if self.lost_target_before:
                    #     self.target_pos_r = (mid_x, mid_y)
                    #     self.head_size = target_size
                    # if first:
                    #     old_mid_x = mid_x
                    # if self.mode == 'left':
                    #     if mid_x >= old_mid_x:
                    #         old_mid_x = mid_x
                    #         self.target_pos_r = target_pos
                    #         self.head_size = target_size
                    # elif self.mode == 'right':
                    #     if mid_x <= old_mid_x:
                    #         old_mid_x = mid_x
                    #         self.target_pos_r = target_pos
                    #         self.head_size = target_size
                    # self.lost_target_before = False
                    # first = False

                if self.body_track and _class == 0:
                    if target_size[1] / SHOT_SIZE[1] > 0.8:
                        continue
                    target_offset = self.cal_offset(target_pos)
                    if target_offset < _offset:
                        _offset = target_offset
                        self.target_pos_r = (mid_x, body_y)
                        self.head_size = target_size
        if self.IMG_VIEW:  # 开启窗口预览
            im0 = annotator.result()
            cv2.circle(im0, self.mouse_rebuild, radius=2, color=(255, 0, 0), thickness=-1)
            if self.pred_pixel_r_pos is not None:
                cv2.circle(im0, self.pred_pixel_r_pos, radius=2, color=(0, 255, 0), thickness=-1)
            if self.pred_rebuild_pixel_pos is not None:
                cv2.circle(im0, self.pred_rebuild_pixel_pos, radius=2, color=(0, 0, 255), thickness=-1)
            scale_percent = 3  # 放大倍数
            width = int(im0.shape[1] * scale_percent)
            height = int(im0.shape[0] * scale_percent)
            resized_image = cv2.resize(im0, (width, height))
            cv2.imshow(window_name, cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))  # 手动转换为RGB输出
            cv2.waitKey(1)
            # Image.fromarray(im0).show()

    def get_target_pos_size(self):
        # if (self.target_xx[0] is not None and self.marker_x_lst != [] and
        #         self.target_xx[0] < self.marker_x_lst[0] < self.target_xx[1]):
        #     return (None, None), (None, None)
        # else:
        return self.target_pos_r, self.head_size

    def cal_offset(self, pos):
        return pow(self.detect_region_pos[0] + pos[0] - self.mouse_x, 2) + pow(
            self.detect_region_pos[1] + pos[1] - self.mouse_y, 2)

    @staticmethod
    def box_iou_xyxy(box1, box2, scale=1):
        # 获取box1左上角和右下角的坐标
        x1min, y1min, x1max, y1max\
            = (1+scale)*box1[0]/2+(1-scale)*box1[2]/2, (1+scale)*box1[1]/2+(1-scale)*box1[3]/2, (1-scale)*box1[0]/2+(1+scale)*box1[2]/2, (1-scale)*box1[1]/2+(1+scale)*box1[3]/2
        # 计算box1的面积
        s1 = (y1max - y1min + 1.) * (x1max - x1min + 1.)
        # 获取box2左上角和右下角的坐标
        x2min, y2min, x2max, y2max\
            = (1+scale)*box2[0]/2+(1-scale)*box2[2]/2, (1+scale)*box2[1]/2+(1-scale)*box2[3]/2, (1-scale)*box2[0]/2+(1+scale)*box2[2]/2, (1-scale)*box2[1]/2+(1+scale)*box2[3]/2
        # 计算box2的面积
        s2 = (y2max - y2min + 1.) * (x2max - x2min + 1.)

        # 计算相交矩形框的坐标
        xmin = np.maximum(x1min, x2min)
        ymin = np.maximum(y1min, y2min)
        xmax = np.minimum(x1max, x2max)
        ymax = np.minimum(y1max, y2max)
        # 计算相交矩形行的高度、宽度、面积
        inter_h = np.maximum(ymax - ymin + 1., 0.)
        inter_w = np.maximum(xmax - xmin + 1., 0.)
        intersection = inter_h * inter_w
        # 计算相并面积
        union = s1 + s2 - intersection
        # 计算交并比
        iou = intersection / union
        return iou

    def get_assist_info(self, pred_pixel_r_pos, mouse_rebuild, pred_rebuild_pixel_pos):
        if pred_pixel_r_pos is not None:
            self.pred_pixel_r_pos = int(pred_pixel_r_pos[0]+160), int(pred_pixel_r_pos[1]+190)
        else:
            self.pred_pixel_r_pos = None
        self.mouse_rebuild = int(mouse_rebuild[0]+160), int(mouse_rebuild[1]+190)
        if pred_rebuild_pixel_pos is not None:
            self.pred_rebuild_pixel_pos = int(pred_rebuild_pixel_pos[0]+160), int(pred_rebuild_pixel_pos[1]+190)
        else:
            self.pred_rebuild_pixel_pos = None

