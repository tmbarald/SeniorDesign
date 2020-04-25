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
import numbers

class LipAnalysis:
    def __init__(self, file):
        # Open the video object with OpenCV
        self.vid = cv2.VideoCapture(file)

        # Reduce the name to only the filename for naiming outputs
        self.filename = os.path.basename(os.path.splitext(file)[0])

        # Load DLib, a lite facial feature detection neural net
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Obtain working path for placing files
        self.full_path = os.getcwd()
        self.path = os.path.join(self.full_path, self.filename)
        # Check if output folder already exists for given filename 
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
            print("Output folder created") # remove this for later
        else:
            print("Output already created")
        
        # Use the current time/date to seperate the files 
        self.now = datetime.datetime.now()

        # In the future we can pass in the filename and use that
        self.path = os.path.join(self.path, 'output_'+ str(self.now.year)+str(self.now.month)+str(self.now.day)+'.csv')
        with open(self.path, 'a', newline='') as csvfile:
            self.spamwriter = csv.writer(csvfile, delimiter=',')
            self.spamwriter.writerow(['Frame', 'Height', 'Width', 'Protrusion', 'Total Area'])

        self.frame_count = 0
        self.pro = 0
        self.height = 0
        self.width = 0
        self.area = 0
        self.prevFrame = None


    def analysis(self):
        # while self.vid.isOpened():
        ret, self.frame = self.vid.read()
        self.frame_count = self.frame_count + 1
        if self.frame is not None:
            self.frame = imutils.resize(self.frame, width=500)
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.rects = self.detector(self.gray, 1)
            for(i, rect) in enumerate(self.rects):
                self.shape = self.predictor(self.gray, rect)
                self.shape = face_utils.shape_to_np(self.shape)
                for(name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                    if name == "mouth":
                        self.clone = self.frame.copy()
                        imgheight, imgwidth, imgchanells = self.clone.shape
                        cv2.putText(self.clone, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # loop over the subset of facial landmarks, drawing the
                        # specific face part
                        self.pts = self.shape[i:j]
                        self.pop = 1
                        self.color = (0, 0, 255)
                        self.white = [255,255,255]
                        #print(pts, " -- ", pop)
                        for (x, y) in self.shape[i:j]:
                            cv2.circle(self.clone, (x, y), 1, self.color, -1)
                            #print(x, " : ", y, " --- ", pop)
                            #important ones are 15 and 19
                            self.top = tuple(self.pts[14])
                            self.bot = tuple(self.pts[18])
                            self.left = tuple(self.pts[12])
                            self.right = tuple(self.pts[16])
                            if self.pop >= 12:
                                self.color = (0, 255, 0)
                            self.pop = self.pop + 1
                        # extract the ROI of the face region as a separate image
                            (x, y, w, h) = cv2.boundingRect(np.array([self.shape[i:j]]))
                            if self.prevFrame is not None and self.pop == 21:
                                plt.clf()
                                plt.cla()
                                for opticalFlow in range(len(self.pts)):
                                # xs = [prevFrame[opticalFlow, 0], pts[opticalFlow, 0]]
                                    #ys = [prevFrame[opticalFlow, 1], pts[opticalFlow, 1]]
                                    self.origin = self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow]
                                    self.u = (self.pts[opticalFlow, 0]) - self.prevFrame[opticalFlow, 0]
                                    self.v = -(self.pts[opticalFlow, 1]) + self.prevFrame[opticalFlow, 1]
                                    if self.v == 0 and self.u == 0:
                                        plt.quiver(self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow, 1], 1, 1, color='r')
                                    else:
                                        plt.quiver(self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow, 1], u, v)
                                    #plt.axes().arrow(prevFrame[opticalFlow, 0], prevFrame[opticalFlow, 1], pts[opticalFlow, 0], pts[opticalFlow, 1], head_width=0.05, head_length=0.1, color='b')
                                    plt.grid(b = True, which='major')
                                    #print(pts[opticalFlow], " ---- ", prevFrame[opticalFlow], " ------ ", frame_count)
                                    #cv2.arrowedLine(frame, tuple(prevFrame[opticalFlow]), tuple(pts[opticalFlow]), (0, 255, 0), 1)
                            self.roi = self.frame[y:y + h, x:x + w]
                            self.roi = imutils.resize(self.roi, width=250, inter=cv2.INTER_CUBIC)
                        # show the particular face part
                            self.area = self.getArea(self.pts)
                            self.height = self.getHeight(self.pts)
                            self.width = self.getWidth(self.pts)
                            self.pro = self.getProtrusion(self.pts, self.frame_count)
                            self.frame_string = "Frame: " + str(self.frame_count)
                            self.area_string = "Area: " + str(self.area)
                            self.height_string = "Height: " + str(self.height)
                            self.width_string = "Width: " + str(self.width)
                            if self.pro is not -1023:
                                self.protusion_string = "Protrusion: " + str(self.pro) + " mm"
                            self.fin = cv2.copyMakeBorder(self.clone.copy(), 0,0,0, 250, cv2.BORDER_CONSTANT, value=(0,0,0))
                            cv2.putText(self.fin, self.frame_string, (imgwidth, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                            cv2.putText(self.fin, self.area_string, (imgwidth, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                            cv2.putText(self.fin, self.width_string, (imgwidth, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                            cv2.putText(self.fin, self.height_string, (imgwidth, 120), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                            cv2.putText(self.fin, self.protusion_string, (imgwidth, 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                            cv2.line(self.fin, self.top, self.bot, (0, 255, 0), 1)
                            cv2.line(self.fin, self.left, self.right, (255, 0, 0), 1)
                            # cv2.imshow("ROI", self.roi)
                            # cv2.imshow("Image", self.fin)
                            if self.frame_count >= 30 and self.pop == 21:
                                plt.gca().invert_yaxis()
                                plt.show()
                            self.filename = os.path.join(self.full_path,self.filename+'_output','frame_'+str(self.frame_count)+'.png')
                            cv2.imwrite(self.filename, self.fin)
                self.prevFrame = self.pts
            with open(self.path, 'a', newline='') as csvfile:
                self.spamwriter = csv.writer(csvfile, delimiter=',')
                self.spamwriter.writerow([str(self.frame_count), str(self.height), str(self.width), str(self.pro), str(self.area)])
        # if cv2.waitKey(1) & 0xFF == ord('q') or self.frame is None:
        #     break
                    # visualize all facial landmarks with a transparent overlay
                    # output = face_utils.visualize_facial_landmarks(frame, shape)
                    # cv2.imshow("Image", output)
            self.roi = np.asanyarray(self.roi)
            self.fin = np.asanyarray(self.fin)
            
            # Pad ROI to match dim of fin
            print(str(self.roi.shape))
            padding = [(250, 250), (132, 132), (0, 0, 0)]
            print(isinstance(padding, float))
            self.roi = np.pad(self.roi, pad_width=padding, mode='constant', constant_values=(self.white))
            print(str(self.roi.shape))
            im = np.hstack(self.roi,self.fin)
            return (1, im)
        # self.vid.release()
        # # Maybe remove this? 
        # cv2.destroyAllWindows()
        return (0, None)

    def getArea(self, points):
        #print(points, " overall points -- ")
        contours = np.array([points[12], points[13], points[14], points[15], points[16], points[17], points[18], points[19]])
        #print(contours, " contours ---")
        area = cv2.contourArea(contours)
        return round(area)


    def getHeight(self, points):
        top = points[14]
        bottom = points[18]

        height = np.linalg.norm(top-bottom)
        return round(height, 0)

    def getWidth(self, points):
        left = points[12]
        right = points[16]

        width = np.linalg.norm(left - right)
        return round(width, 0)

    def getProtrusion(self, points, frame_count):
        # in future, pass in the file name to get the correct depth files
        # This needs figuring out
        try:
            f = os.path.join(self.full_path, self.filename, 'depth_out', 'frame' + str(frame_count) + '.npy')    
            frame_depth = np.load(f)
            top_mid = frame_depth[points[3,0], points[3,1]]
            top_bot = frame_depth[points[14,0], points[14,1]]

            avg_dist = 0
            for i in range(0, 19):
                avg_dist = avg_dist + frame_depth[points[i, 0], points[i,1]]

            avg_dist = avg_dist / 20
            # Maybe change this function to return another value
            return top_mid - avg_dist
        except:
            print("No Depth data found for the selected video!")
            return -1023

