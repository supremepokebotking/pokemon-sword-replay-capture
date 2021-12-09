import numpy as np
import cv2

def open_cam_usb(dev):
    # We want to set width and height here, otherwise we could just do:
    #     return cv2.VideoCapture(dev)
    gst_str = ("v4l2src device=/dev/video{} ! "
	       "image/jpeg, format=(string)RGGB ! "
	       " jpegdec ! videoconvert ! queue ! appsink").format(dev)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

cap = cv2.VideoCapture(0) # check this

#cap = open_cam_usb("2")

gst_str = ("v4l2src device=/dev/video2 ! "
       "image/jpeg, format=(string)RGGB ! "
       " jpegdec ! videoconvert ! queue ! appsink")
#cap=cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

import time
time.sleep(1)
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
