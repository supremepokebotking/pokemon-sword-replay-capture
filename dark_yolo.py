#############################################
# Object detection - YOLO - OpenCV
# Author : Arun Ponnusamy   (July 16, 2018)
# Website : http://www.arunponnusamy.com
############################################


import cv2
import argparse
import numpy as np
import random

import os
import sys, os
sys.path.append('/Users/Curtis/Documents/darknet/python')

import darknet2 as dn


def array_to_image(arr):
    arr = arr.transpose(2,0,1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = (arr/255.0).flatten()
    data = dn.c_array(dn.c_float, arr)
    im = dn.IMAGE(w,h,c,data)
    return im

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

class YOLO(object):
    _defaults = {
#        "model_path": b"model_data/yolo-obj-416_10000.weights",
#        "config_path": b"model_data/yolo-obj-416.cfg",
#        "model_path": b"model_data/yolo-obj-416-shrunk_80000.weights",
#        "config_path": b"model_data/yolo-obj-416-shrunk.cfg",
#        "model_path": b"model_data/yolov3_med-416_20000.weights",
#        "config_path": b"model_data/yolov3_med-416.cfg",
        "model_path": b"model_data/yolov3_med-416_70000.weights",
        "config_path": b"model_data/yolov3_med-416.cfg",
        "meta_path": b"model_data/obj.data",
        "classes_path": 'model_data/obj.names',
        "score" : 0.8,
        "iou" : 0.9,
        "frame_count": 0,
        "model_image_size" : (416, 416),
        "gpu_num" : 1,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults) # set up default values
        self.__dict__.update(kwargs) # and update with user overrides
        self.classes = self._get_class()

        self.COLORS = np.random.uniform(0, 255, size=(len(self.classes), 3))

        #net = cv2.dnn.readNet(args.weights, args.config)
        self.net = dn.load_net(self.config_path,self.model_path, 0)
        self.meta = dn.load_meta(self.meta_path)

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names



    def get_output_layers(self):

        layer_names = self.net.getLayerNames()

        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

        return output_layers


    def draw_prediction(self, img, class_name, x, y, x_plus_w, y_plus_h):

        class_id = self.classes.index(class_name)

        color = self.COLORS[class_id]
    #    color = (255, 0, 0)

        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

        cv2.putText(img, class_name, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    def process_image(self, cv_image, add_boxes=True, show_image=False):

        thresh=.5
        hier_thresh=.5
        nms=.45

        Width = cv_image.shape[1]
        Height = cv_image.shape[0]
        scale = 1/255.0
#        scale = 1/512.0
#        scale = 1/736.0
#        scale = 1/1024.0
#        scale = 1/1280.0

        image = array_to_image(cv_image)
        dn.rgbgr_image(image)
        num = dn.c_int(0)
        pnum = dn.pointer(num)
        dn.predict_image(self.net, image)
        dets = dn.get_network_boxes(self.net, image.w, image.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (nms): dn.do_nms_obj(dets, num, self.meta.classes, nms);

        res = []
        for j in range(num):
            for i in range(self.meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    res.append((self.meta.names[i].decode('ascii'), dets[j].prob[i], (b.x, b.y, b.w, b.h)))
        res = sorted(res, key=lambda x: -x[1])

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        labels_and_boxes = {}


        for r in res:
            name, p, box = r
            x, y, w, h = box
#            if p < self.score:
#                continue


            xmin, ymin, xmax, ymax = convertBack(float(x), float(y), float(w), float(h))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)

            if add_boxes:
                self.draw_prediction(cv_image, name, xmin, ymin, xmax, ymax)

            label = name
            battle_state = None
            battle_selectable = None
            submenu_selectable = None

            if label not in labels_and_boxes:
                labels_and_boxes[label] = []
            boxes_for_label = labels_and_boxes[label]
            boxes_for_label.append([xmin, ymin, xmax, ymax])


        if show_image:
            cv2.imshow("object detection", image)
            cv2.waitKey()

        save_file = "object_detection_%d.jpg" % (self.frame_count)
        self.frame_count += 1
#        cv2.imwrite(save_file, image)
        if show_image:
            cv2.destroyAllWindows()
        return labels_and_boxes
