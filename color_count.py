import cv2
import numpy as np
import matplotlib.pyplot as mp

cap = cv2.VideoCapture(1)
#cap = cv2.VideoCapture('hotgif.gif')
#cap = cv2.VideoCapture('green.mp4')
green_over_time = []
#frames_over_time = []
time = []

frames = 0
fps = cap.get(cv2.CAP_PROP_FPS)
print fps

while(cap.isOpened()):
    ret, frame = cap.read()

    test = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

   ## mask = cv2.inRange(test, (50, 50,50), (80,255,255))
    mask1 = cv2.inRange(test, (0,50,20), (5,255,255))
    mask2 = cv2.inRange(test, (175,50,20), (180,255,255))
    mask = cv2.bitwise_or(mask1, mask2)
    croped = cv2.bitwise_and(frame, frame, mask=mask)
    green_pixels = np.count_nonzero(croped);
    size = round(green_pixels * 100 / croped.size, 3)
    green_over_time.append(size)
    time.append(frames/fps)
    frames = frames + 1
    #cv2.imshow("cap", cap)
    cv2.imshow("croped", croped)
    cv2.resizeWindow("croped", 1300,700)
   # cv2.namedWindow("croped", cv2.WINDOW_NORMAL)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
mp.plot(time, green_over_time)
mp.grid()
mp.xlabel('Time (Seconds)')
mp.ylabel('Number of green pixels')
mp.title('Sample Area chart')
mp.show()



