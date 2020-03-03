import cv2
from PIL import ImageTk, Image
import numpy as np
import pyrealsense2 as rs
from imutils import face_utils
import dlib
import imutils
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import csv
import datetime


def getArea(points):
    #print(points, " overall points -- ")
    contours = np.array([pts[12], pts[13], pts[14], pts[15], pts[16], pts[17], pts[18], pts[19]])
    #print(contours, " contours ---")
    area = cv2.contourArea(contours)
    return round(area)


def getHeight(points):
    top = points[14]
    bottom = points[18]

    height = np.linalg.norm(top-bottom)
    return round(height, 0)

def getWidth(points):
    left = points[12]
    right = points[16]

    width = np.linalg.norm(left - right)
    return round(width, 0)


vid = cv2.VideoCapture('test.avi')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

full_path = os.getcwd()
path = os.path.join(full_path, "test_output")
if not os.path.isdir(path):
    os.mkdir(path)
    print("Output folder created") # remove this for later
else:
    print("output already created")
now = datetime.datetime.now()
path = os.path.join(path, 'output_'+ str(now.year)+str(now.month)+str(now.day)+'.csv')
with open(path, 'a', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['Frame', 'Height', 'Width', 'Protrusion', 'Total Area'])

frame_count = 0
pro = 0
height = 0
width = 0
area = 0
prevFrame = None

while vid.isOpened():
    ret, frame = vid.read()
    frame_count = frame_count + 1
    if frame is not None:
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)
        for(i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            for(name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                if name == "mouth":
                    clone = frame.copy()
                    imgheight, imgwidth, imgchanells = clone.shape
                    cv2.putText(clone, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    # loop over the subset of facial landmarks, drawing the
                    # specific face part
                    pts = shape[i:j]
                    pop = 1
                    color = (0, 0, 255)
                    white = [255,255,255]
                    #print(pts, " -- ", pop)
                    for (x, y) in shape[i:j]:
                        cv2.circle(clone, (x, y), 1, color, -1)
                        #print(x, " : ", y, " --- ", pop)
                        #important ones are 15 and 19
                        top = tuple(pts[14])
                        bot = tuple(pts[18])
                        left = tuple(pts[12])
                        right = tuple(pts[16])
                        if pop >= 12:
                            color = (0, 255, 0)
                        pop = pop + 1
                    # extract the ROI of the face region as a separate image
                        (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
                        if prevFrame is not None and pop == 21:
                            plt.clf()
                            plt.cla()
                            for opticalFlow in range(len(pts)):
                               # xs = [prevFrame[opticalFlow, 0], pts[opticalFlow, 0]]
                                #ys = [prevFrame[opticalFlow, 1], pts[opticalFlow, 1]]
                                origin = prevFrame[opticalFlow, 0], prevFrame[opticalFlow]
                                u = (pts[opticalFlow, 0]) - prevFrame[opticalFlow, 0]
                                v = -(pts[opticalFlow, 1]) + prevFrame[opticalFlow, 1]
                                if v == 0 and u == 0:
                                    plt.quiver(prevFrame[opticalFlow, 0], prevFrame[opticalFlow, 1], 1, 1, color='r')
                                else:
                                    plt.quiver(prevFrame[opticalFlow, 0], prevFrame[opticalFlow, 1], u, v)
                                #plt.axes().arrow(prevFrame[opticalFlow, 0], prevFrame[opticalFlow, 1], pts[opticalFlow, 0], pts[opticalFlow, 1], head_width=0.05, head_length=0.1, color='b')
                                plt.grid(b = True, which='major')
                                #print(pts[opticalFlow], " ---- ", prevFrame[opticalFlow], " ------ ", frame_count)
                                #cv2.arrowedLine(frame, tuple(prevFrame[opticalFlow]), tuple(pts[opticalFlow]), (0, 255, 0), 1)
                        roi = frame[y:y + h, x:x + w]
                        roi = imutils.resize(roi, width=250, inter=cv2.INTER_CUBIC)
                    # show the particular face part
                        area = getArea(pts)
                        height = getHeight(pts)
                        width = getWidth(pts)
                        frame_string = "Frame: " + str(frame_count)
                        area_string = "Area: " + str(area)
                        height_string = "Height: " + str(height)
                        width_string = "Width: " + str(width)
                        protusion_string = "Protrusion: " + str(pro)
                        fin = cv2.copyMakeBorder(clone.copy(), 0,0,0, 250, cv2.BORDER_CONSTANT, value=(0,0,0))
                        cv2.putText(fin, frame_string, (imgwidth, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(fin, area_string, (imgwidth, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(fin, width_string, (imgwidth, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(fin, height_string, (imgwidth, 120), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(fin, protusion_string, (imgwidth, 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.line(fin, top, bot, (0, 255, 0), 1)
                        cv2.line(fin, left, right, (255, 0, 0), 1)
                        cv2.imshow("ROI", roi)
                        cv2.imshow("Image", fin)
                        if frame_count >= 30 and pop == 21:
                            plt.gca().invert_yaxis()
                            plt.show()
                        filename = os.path.join(full_path,'test_output','frame_'+str(frame_count)+'.png')
                        cv2.imwrite(filename, fin)
            prevFrame = pts
    with open(path, 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow([str(frame_count), str(height), str(width), str(pro), str(area)])
    if cv2.waitKey(1) & 0xFF == ord('q') or frame is None:
        break
                    # visualize all facial landmarks with a transparent overlay
                #output = face_utils.visualize_facial_landmarks(frame, shape)
                #cv2.imshow("Image", output)
"""
    def getArea(points):
 #       print(points, " overall points -- ")
        contours = np.array([pts[12], pts[13], pts[14], pts[15], pts[16], pts[17], pts[18], pts[19]])
#        print(contours, " contours ---")
        area = cv2.contourArea(contours)
        return round(area)


    def getHeight(points):
        top = points[14]
        bottom = points[18]

        height = np.linalg.norm(top-bottom)
        return round(height, 0)

    def getWidth(points):
        left = points[12]
        right = points[16]

        width = np.linalg.norm(left - right)
        return round(width, 0)
"""
#    cv2.imshow('frame', frame


vid.release()
cv2.destroyAllWindows()

