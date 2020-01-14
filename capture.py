import cv2
import numpy as np

#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('hotgif.gif')
#cap = cv2.VideoCapture('green.mp4')
#green_over_time = []
#frames_over_time = []
#time = []

#frames = 0
#fps = cap.get(cv2.CAP_PROP_FPS)
#print(fps)

def run_cap():
    print("hello boooi")
    cap = cv2.VideoCapture(1)
    fps = cap.get(cv2.CAP_PROP_FPS)
    while(cap.isOpened()):
       ret, frame = cap.read()
       cv2.imshow("frame", frame)
       if((cv2.waitKey(1) & 0xFF == ord('q')) or  (cv2.getWindowProperty('frame', 0) == -1)):
           break

    cap.release()
    cv2.destroyAllWindows()


