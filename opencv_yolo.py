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

class YOLO(object):
    _defaults = {
        "model_path": "model_data/yolov3_med-416_30000.weights",
        "config_path": "model_data/yolov3_med-416.cfg",
#        "model_path": "model_data/yolo-obj-416-shrunk_10000.weights",
#        "config_path": "model_data/yolo-obj-416-shrunk.cfg",
        "meta_path": "model_data/obj.data",
        "classes_path": 'model_data/obj.names',
        "score" : 0.5,
        "iou" : 0.6,
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
        self.net = cv2.dnn.readNetFromDarknet(self.config_path, self.model_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

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


    def draw_prediction(self, img, class_id, confidence, x, y, x_plus_w, y_plus_h):

        label = str(self.classes[class_id])

        color = self.COLORS[class_id]
    #    color = (255, 0, 0)
        x = int(x)
        y = int(y)
        x_plus_w = int(x_plus_w)
        y_plus_h = int(y_plus_h)

#        print(label)

        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

        cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    def process_image(self, image, add_boxes=False, show_image=False):

        Width = image.shape[1]
        Height = image.shape[0]
        scale = 1/255.0
#        scale = 1/512.0
#        scale = 1/416.0
#        scale = 1/1024.0
#        scale = 1/1280.0

        classes = None

#        print(self.model_image_size[0])
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

        self.net.setInput(blob)

        outs = self.net.forward(self.get_output_layers())

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.4
#        conf_threshold = self.score
        nms_threshold = 0.4

        labels_and_boxes = {}


        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > conf_threshold:
                    label = str(self.classes[class_id])
                    #print(label)

                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))

                    x1=int(center_x-w * 0.5)
                    y1=int(center_y-h * 0.5)
                    x2=int(center_x+w * 0.5)
                    y2=int(center_y+h * 0.5)

                    boxes.append([x, y, w, h])
        #            boxes.append([x1, y1, x2, y2])
#                    cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),1)


        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        for i in indices:

            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]

            label = str(self.classes[class_ids[i]])
            battle_state = None
            battle_selectable = None
            submenu_selectable = None

            if label not in labels_and_boxes:
                labels_and_boxes[label] = []
            boxes_for_label = labels_and_boxes[label]
            boxes_for_label.append([x, y, x+w, y+h])
#            cv2.rectangle(image, (int(1039),int(409)), (int(1039+230),int(409+72)), (255,255,255), 2)
        #    draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(w), round(h))
            if add_boxes:
                self.draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))


        if show_image:
            cv2.imshow("object detection", image)
            cv2.waitKey()

        save_file = "object_detection_%d.jpg" % (self.frame_count)
        self.frame_count += 1
#        cv2.imwrite(save_file, image)
        if show_image:
            cv2.destroyAllWindows()
        return labels_and_boxes
