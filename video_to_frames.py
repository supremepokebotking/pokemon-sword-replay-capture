import cv2
import numpy as np

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture('test_videos/shadow_tag_volt_switch_choice_specs_battle.mov')
image_count = 0

# Check if camera opened successfully
if (cap.isOpened()== False):
  print("Error opening video stream or file")

frames = 0
# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  frames += 1
  if ret == True:
    if not (frames % 20 == 0):
      continue

    frame = cv2.resize(frame, (1280, 720), interpolation = cv2.INTER_AREA)

    image_count_str = str(image_count)
    if len(image_count_str) == 1:
        image_count_str = '00%s' % image_count_str
    if len(image_count_str) == 2:
        image_count_str = '0%s' % image_count_str

    save_file = "framed_shadow_tag_volt_switch_choice_specs_battle/frame%s.jpg" % (image_count_str)
    image_count += 1
    cv2.imwrite(save_file, frame)

  # Break the loop
  else:
    break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
