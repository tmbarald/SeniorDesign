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
print(fps)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, fourcc, 30.0, (640, 480))


while(cap.isOpened()):
    ret, frame = cap.read()
    #convert frame of video cap to HSV spectrum
    test = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #range of green pixels (play with)
    mask = cv2.inRange(test, (25, 25, 25), (80, 255, 255))
    croped = cv2.bitwise_and(frame, frame, mask=mask)
    gray = cv2.cvtColor(croped, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray", gray)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((4,4), np.uint8)
    dilation = cv2.dilate(edges, kernel, iterations=1)
    minLineLength = 11
    maxLineGap = 10
    lines = cv2.HoughLinesP(dilation, 1, np.pi / 180, 50, minLineLength, maxLineGap)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # Display the result.
    cv2.imwrite('h_frame.png', frame)
    cv2.imshow('frame', frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
