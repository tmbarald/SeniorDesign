import numpy as np
import cv2

cv2.namedWindow("preview")

out = cv2.VideoWriter('output.mp4', -1, 20.0, (640 ,480))
vc = cv2.VideoCapture(1)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    rval, frame = vc.read()
    out.write(frame)
    cv2.imshow("preview", frame)
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
out.release()
vc.release()