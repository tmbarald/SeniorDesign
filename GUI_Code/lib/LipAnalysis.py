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
        self.predictor = dlib.shape_predictor(''./ib/shape_predictor_68_face_landmarks.dat')

        # Obtain working path for placing files
        self.full_path = os.getcwd()
        self.path = os.path.join(self.full_path, self.filename)
        self.img_dir = os.path.join(self.path, 'images')
        self.depth_dir = os.path.join(self.path, 'depth_out')
        # Check if output folder already exists for given filename
        try:
            os.mkdir(self.path)
        except:
            pass
        
        # Also make sub-directory to store iamges
        try:
            os.mkdir(self.img_dir) 
        except:
            pass
        
        # Use the current time/date to seperate the files 
        self.now = datetime.datetime.now()

        # In the future we can pass in the filename and use that
        self.csv = os.path.join(self.path, 'output_'+ str(self.now.year)+str(self.now.month)+str(self.now.day)+'.csv')
        with open(self.csv, 'a', newline='') as csvfile:
            self.spamwriter = csv.writer(csvfile, delimiter=',')
            self.spamwriter.writerow(['Frame', 'Height', 'Width', 'Protrusion', 'Total Area'])

        ## Global variables for control
        self.frame_count = 0
        self.pro = 0
        self.height = 0
        self.width = 0
        self.area = 0
        self.prevFrame = None
        self.open_file_attempt = True

        ## Global varaible to store plot in, lowers memory usage by reusing same obj
        self.fig = plt.figure()
        self.fig.add_subplot(111)
        self.fig.tight_layout(pad=1)
        self.plot = None


    def analysis(self):
        ## Perform the lip analysis on the video obj passed to the class
        ## Open the video object and retreive frames
        ret, self.frame = self.vid.read()
        ## Keep counter of frame count
        self.frame_count = self.frame_count + 1
        ## Perform analysis so long as there is a frame
        if self.frame is not None:
            ## Resize the frame and convert to grayscale
            self.frame = imutils.resize(self.frame, width=500)
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            ## Feed grayscale image to face detecter neural net
            self.rects = self.detector(self.gray, 1)
            ## Iterate through the possible features found by the detector
            for(i, rect) in enumerate(self.rects):
                ## Use predictor to guess facial features (dlib)
                self.shape = self.predictor(self.gray, rect)
                self.shape = face_utils.shape_to_np(self.shape)
                ## Iterate through the features predicted by the neural net
                for(name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                    ## Only concerned by the 'mouth' feature
                    if name == "mouth":
                        ## Use a copy of the frame
                        self.clone = self.frame.copy()
                        imgheight, imgwidth, imgchanells = self.clone.shape
                        cv2.putText(self.clone, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # Loop over the subset of facial landmarks, drawing the
                        # specific face part
                        self.pts = self.shape[i:j]
                        self.pop = 1
                        self.color = (0, 0, 255)
                        self.white = [255,255,255]
                        ## Loop over the specific lip points
                        for (x, y) in self.shape[i:j]:
                            cv2.circle(self.clone, (x, y), 1, self.color, -1)
                            #important ones are 15 and 19
                            self.top = tuple(self.pts[14])
                            self.bot = tuple(self.pts[18])
                            self.left = tuple(self.pts[12])
                            self.right = tuple(self.pts[16])
                            if self.pop >= 12:
                                self.color = (0, 255, 0)
                            self.pop = self.pop + 1
                            ## Extract the ROI of the face region as a separate image
                            (x, y, w, h) = cv2.boundingRect(np.array([self.shape[i:j]]))
                            if self.prevFrame is not None and self.pop == 21:
                                ## Create plot of lip movement
                                plt.clf()
                                plt.cla()
                                for opticalFlow in range(len(self.pts)):
                                    self.origin = self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow]
                                    self.u = (self.pts[opticalFlow, 0]) - self.prevFrame[opticalFlow, 0]
                                    self.v = -(self.pts[opticalFlow, 1]) + self.prevFrame[opticalFlow, 1]
                                    if self.v == 0 and self.u == 0:
                                        plt.quiver(self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow, 1], 1, 1, color='r')
                                    else:
                                        plt.quiver(self.prevFrame[opticalFlow, 0], self.prevFrame[opticalFlow, 1], self.u, self.v)
                                    plt.grid(b = True, which='major')
                        self.roi = self.frame[y:y + h, x:x + w]
                        self.roi = imutils.resize(self.roi, width=250, inter=cv2.INTER_CUBIC)
                        ## Calculate lip parameters from extracted lip data
                        self.area = self.getArea(self.pts)
                        self.height = self.getHeight(self.pts)
                        self.width = self.getWidth(self.pts)
                        self.pro = self.getProtrusion(self.pts, self.frame_count)
                        self.frame_string = "Frame: " + str(self.frame_count)
                        self.area_string = "Area: " + str(self.area)
                        self.height_string = "Height: " + str(self.height)
                        self.width_string = "Width: " + str(self.width)
                        ## Add border, then add lip parameter details to the image
                        self.fin = cv2.copyMakeBorder(self.clone.copy(), 0,0,0, 250, cv2.BORDER_CONSTANT, value=(0,0,0))
                        cv2.putText(self.fin, self.frame_string, (imgwidth, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                        cv2.putText(self.fin, self.area_string, (imgwidth, 60), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                        cv2.putText(self.fin, self.width_string, (imgwidth, 90), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                        cv2.putText(self.fin, self.height_string, (imgwidth, 120), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                        ## Depth data may not always be available
                        if self.pro is not None:
                            self.protusion_string = "Protrusion: " + str(self.pro) + " mm"
                            cv2.putText(self.fin, self.protusion_string, (imgwidth, 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, self.color, 2)
                        else:
                            self.open_file_attempt = False
                        ## Draw lines indicating lip cross section
                        cv2.line(self.fin, self.top, self.bot, (0, 255, 0), 1)
                        cv2.line(self.fin, self.left, self.right, (255, 0, 0), 1)
                        ## After enough data, begin graphing the lip movement
                        if self.frame_count >= 30 and self.pop == 21:
                            plt.gca().invert_yaxis()
                            self.fig.suptitle('Lip Movement')
                            ## Begin the process of converting from matplotlib plot to
                            ## a numpy array so it can be veiwed as an image
                            self.fig.canvas.draw()
                            self.plot = np.fromstring(self.fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
                            self.plot = self.plot.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
                            self.plot = imutils.resize(self.plot, width = 530)
                        ## Save the images with the data on them into their own sub-directory    
                        cv2.imwrite(os.path.join(self.img_dir, 'frame_'+str(self.frame_count)+'.png'), self.fin)
                ## Save the previous points for lip movement calculations
                self.prevFrame = self.pts
            ## Write the lip data into a csv file
            with open(self.csv, 'a', newline='') as csvfile:
                self.spamwriter = csv.writer(csvfile, delimiter=',')
                self.spamwriter.writerow([str(self.frame_count), str(self.height), str(self.width), str(self.pro), str(self.area)])
            ## Return success and the images; convert from BGR to RGB
            try:
                return (1, cv2.cvtColor(self.fin, cv2.COLOR_BGR2RGB), cv2.cvtColor(self.roi, cv2.COLOR_BGR2RGB), self.plot)
            except Exception as e:
                print('No face detected in the first frame, please make sure the camera is correctly aligned and try again.')
                print(e)
                
        ## Else, could not open video of there are no more frames to read
        plt.close(self.fig)
        return (0, None, None, None)

    ## Find the area between left, right, top and bottom points
    def getArea(self, points):
        ## Get outline of lips
        contours = np.array([points[12], points[13], points[14], points[15], points[16], points[17], points[18], points[19]])
        ## Find the area encompassed by points
        area = cv2.contourArea(contours)
        return round(area)

    ## Find the height between top and bottom points
    def getHeight(self, points):
        ## Top and bottom most points
        top = points[14]
        bottom = points[18]
        ## Compute distance between these points
        height = np.linalg.norm(top-bottom)
        return round(height, 0)

    ## Find the width between left and right points
    def getWidth(self, points):
        ##  Use the left and right most points
        left = points[12]
        right = points[16]
        ## Compute distance between these points
        width = np.linalg.norm(left - right)
        return round(width, 0)

    def getProtrusion(self, points, frame_count):
        # This needs figuring out to produce more reliable answers
        if self.open_file_attempt:
            try:
                ## Try to find and open the first frame depth data
                f = os.path.join(self.depth_dir, 'frame' + str(frame_count) + '.npy')    
                frame_depth = np.load(f)
                ## Get the depth values from the relative points
                top_mid = frame_depth[points[3,0], points[3,1]]
                top_bot = frame_depth[points[14,0], points[14,1]]
                ## Compute the average distance to lips
                avg_dist = 0
                for i in range(0, 19):
                    avg_dist = avg_dist + frame_depth[points[i, 0], points[i,1]]

                ## top mid minus the average
                avg_dist = avg_dist // 20
                # Maybe change this function to return another value
                return top_mid - avg_dist
            except:
                print("No Depth data found for the selected video!")
                return None
        else:
            return None