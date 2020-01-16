import tkinter as tk
import os
import sys
import cv2
from PIL import ImageTk, Image
import time
import numpy as np

#video class
class VideoCapture:
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

    #update camera
    def get_frame(self):
        #camera is running
        if self.vid.isOpened():
            #grab current fram
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    #destructor
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
