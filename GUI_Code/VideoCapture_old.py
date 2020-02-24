import cv2
from PIL import ImageTk, Image
import time
import numpy as np
import pyrealsense2 as rs


#video class
class VideoCapture_old:
    def __init__(self,sourceCam):

        #getting the webcam
        self.vid = cv2.VideoCapture(sourceCam)
        if not self.vid.isOpened():
            raise ValueError("source is wrong", 0)

        #resolution of the camera
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        #sets canvas to max width and height of captured video
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FOURCC, 0x32595559)
        #not sure if we need this to set fps
        #self.vid.set(cv2.CAP_PROP_FPS, 15)

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #self.out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, self.fourcc, 30.0, (640,480))

    #update camera
    def get_frame(self, isRecording):

        #camera is running
        if self.vid.isOpened():
            #grab current frame
            ret, frame = self.vid.read()
            if ret:
                if isRecording:
                    self.out.write(frame)
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                raise ValueError("Video stream connection interrupted!", None)
        else:
            return (ret, None)
    
    #create new video writer object to write video frames
    def new_writer(self):
       self.out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, self.fourcc, 30.0, (640,480)) 

    def close_writer(self):
        self.out.release()

    #destructor
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    