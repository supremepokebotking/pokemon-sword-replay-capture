# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

from scipy.misc import imread
import cv2

def array_to_image(arr):
    arr = arr.transpose(2,0,1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = (arr/255.0).flatten()
    data = dn.c_array(dn.c_float, arr)
    im = dn.IMAGE(w,h,c,data)
    return im

def detect2(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
#    boxes = dn.make_boxes(net)
#    probs = dn.make_probs(net)
    res = dn.detect(net, meta, image)

    for r in range(res):
        name, x, y, w, h = r
        x_plus_w = int(x + w)
        y_plus_h = int(y + h)
        cv2.rectangle(image, (x,y), (x_plus_w,y_plus_h), (255, 255, 255), 2)
    res = sorted(res, key=lambda x: -x[1])
    dn.free_ptrs(dn.cast(probs, dn.POINTER(dn.c_void_p)), num)
    return res

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def detect3(net, meta, cv_image, thresh=.5, hier_thresh=.5, nms=.45):
    image = array_to_image(cv_image)
    dn.rgbgr_image(image)
    num = dn.c_int(0)
    pnum = dn.pointer(num)
    dn.predict_image(net, image)
    dets = dn.get_network_boxes(net, image.w, image.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): dn.do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])

    for r in res:
        name, p, box = r
        x, y, w, h = box
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        xmin, ymin, xmax, ymax = convertBack(float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)

        print(x)
        print(y)
        print(w)
        print(h)
        print(type(image))
        print(image)
        x_plus_w = int(x + w)
        y_plus_h = int(y + h)
        print(x_plus_w)
        print(y_plus_h)
        cv2.rectangle(cv_image, (x,y), (x_plus_w,y_plus_h), (255, 255, 255), 2)
        cv2.rectangle(cv_image, pt1, pt2, (0, 255, 0), 2)

    dn.free_detections(dets, num)
    return res


import sys, os
sys.path.append('/Users/Curtis/Documents/darknet/python')

import darknet2 as dn

# Darknet
#net = dn.load_net("cfg/tiny-yolo.cfg", "tiny-yolo.weights", 0)
#meta = dn.load_meta("cfg/coco.data")
net = dn.load_net(b"model_data/yolo-obj-old-416.cfg", b"model_data/yolo-obj-old-410_5600.backup", 0)
meta = dn.load_meta(b"model_data/obj-old.data")

r = dn.detect(net, meta, b"test_images/check_active_1.jpg")
print(r)

# scipy
#arr= imread("test_images/check_active_1.jpg")
#im = array_to_image(arr)
#r = detect3(net, meta, im)
#cv2.imwrite("scipy.misc-object-detection.jpg", im)
#print(r)

images = ['check_pokemon_stats_1.jpg', 'check_pokemon_stats_2.jpg', 'check_pokemon_stats_3.jpg', 'check_pokemon_stats_4.jpg', 'check_pokemon_stats_5.jpg', 'check_pokemon_stats_6.jpg', 'check_pokemon_stats_7.jpg', 'check_pokemon_stats_8.jpg', 'check_pokemon_stats_9.jpg']

image_count = 0
for image_name in images:
    # OpenCV
    arr = cv2.imread("test_images/%s" % (image_name))
#    arr = cv2.imread("test_images/check_active_1.jpg")
    r = detect3(net, meta, arr)
#    cv2.imwrite("cv-object-detection.jpg", arr)
    save_file = "cv-object-object_detection_%d.jpg" % (image_count)
    image_count += 1
    cv2.imwrite(save_file, arr)
    print(r)
