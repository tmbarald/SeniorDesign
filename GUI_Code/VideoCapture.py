import tkinter.filedialog
import tkinter as tk
import cv2
from PIL import ImageTk, Image
import time
import numpy as np
import pyrealsense2 as rs


#video class
class VideoCapture:
    def __init__(self,sourceCam):

        self.videoType = 'XVID'
        self.width  = 640
        self.height = 480
        self.fps    = 60
        self.fileName = 'default'
                
        self.pipeline = rs.pipeline()        
        self.config   = rs.config()
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, self.fps)
        
        self.pipeline.start(self.config)

        #Saving the file
        self.fourcc    = cv2.VideoWriter_fourcc(*self.videoType)
        self.color_out = cv2.VideoWriter('color_out.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))
        self.depth_out = cv2.VideoWriter('depth_out.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))

    #update camera
    def get_frame(self, isRecording):
        
        #wait for frames from d435
        frames      = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)

        #saves RGB and depth videos to two different files
        if isRecording:
            self.color_out.write(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
            self.depth_out.write(depth_colormap)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))
        return (1, images)


    #create new video writer object to write video frames
    def new_writer(self):
       self.color_out = cv2.VideoWriter(self.fileName + 'color_out.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))
       self.depth_out = cv2.VideoWriter(self.fileName + 'depth_out.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))

    def close_writer(self):
        self.color_out.release()
        self.depth_out.release()

    def save(self):
        self.fileName = tk.filedialog.asksaveasfilename(initialdir = "/", title = "Save As",filetypes =[("Video files","*.avi")])
        
    #destructor
    def __del__(self):
        self.pipeline.stop()
    