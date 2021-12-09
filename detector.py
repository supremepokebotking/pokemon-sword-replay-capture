# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

import sys, os
#sys.path.append(os.path.join(os.getcwd(),'python/'))
sys.path.append('/Users/Curtis/Documents/darknet/python')


import darknet2 as dn
import pdb

#dn.set_gpu(0)
net = dn.load_net(b"model_data/yolo-obj-old-416.cfg", b"model_data/yolo-obj-old-410_5600.backup", 0)
meta = dn.load_meta(b"model_data/obj-old.data")
r = dn.detect(net, meta, b"test_images/check_active_1.jpg")
print(r)


"""
# And then down here you could detect a lot more images like:
r = dn.detect(net, meta, "data/eagle.jpg")
print r
r = dn.detect(net, meta, "data/giraffe.jpg")
print r
r = dn.detect(net, meta, "data/horses.jpg")
print r
r = dn.detect(net, meta, "data/person.jpg")
print r
"""
