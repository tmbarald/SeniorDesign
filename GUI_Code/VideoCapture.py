import cv2
from PIL import ImageTk, Image
import time
import numpy as np
import pyrealsense2 as rs


#video class
class VideoCapture:
    def __init__(self,sourceCam):

        self.width = 640
        self.height = 480
        self.fps = 30

        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, self.fps)
        
        self.pipeline.start(self.config)

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #update camera
    def get_frame(self, isRecording):
        
        #wait for frames from d435
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        frame = np.hstack((color_image, depth_colormap))
        
        if isRecording:
            self.out.write(frame)
        
        return (1, frame)
    
    #create new video writer object to write video frames
    def new_writer(self):
       self.out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height)) 

    def close_writer(self):
        self.out.release()

    #destructor
    def __del__(self):
        self.pipeline.stop()
    