import tkinter as tk
import os
import sys
import cv2
from PIL import ImageTk, Image
import time
import numpy as np

#video class
class VideoCapture:
    def __init__(self):
        self.vid = cv2.VideoCapture(1)
        if not self.vid.isOpened():
            raise ValueError("source is wrong", 0)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FOURCC, 0x32595559)
        self.vid.set(cv2.CAP_PROP_FPS, 15)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()