import tkinter.filedialog
import tkinter as tk
import cv2
from PIL import ImageTk, Image
import time
import numpy as np
import pyrealsense2 as rs
import os
import csv
import datetime

full_path = os.getcwd()
if not os.path.isdir(full_path + "\\depth_out"):
    path = os.path.join(full_path, "depth_out")
    os.mkdir(path)
    print("Output folder created") # remove this for later
now = datetime.datetime.now()



#video class
class VideoCapture:
    def __init__(self,sourceCam):

        self.videoType  = 'XVID'
        self.width      = 640
        self.height     = 480
        self.fps        = 30
        self.fileName   = 'default'
        self.frame_num  = 0
        self.depth_dict = dict()
        
        ''' 
        #   Not sure on how to use these filters in Python 
        #   https://github.com/IntelRealSense/librealsense/tree/master/examples/measure 

        # Processing blocks
        self.dec = rs.decimation_filter()
        self.dec.set_option(rs.option.filter_magnitude, 8)
        self.spat = rs.spatial_filter()
        self.spat.set_option(rs.option.holes_fill, 5)
        self.temp = rs.temporal_filter()
        '''

        self.pipeline   = rs.pipeline()        
        self.config     = rs.config()
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, self.fps)
        
        self.profile    = self.pipeline.start(self.config)

        #Saving the file
        self.fourcc         = cv2.VideoWriter_fourcc(*self.videoType)
        self.depth_sensor   = self.profile.get_device().first_depth_sensor()
        self.depth_sensor.set_option(rs.option.visual_preset, 2)

        '''
        # Used to get depth scale
        self.depth_scale = self.depth_sensor.get_depth_scale()
        print("Depth scale is: ", self.depth_scale)
        self.clipping_distance_in_meters = 1
        self.clipping_distance = self.clipping_distance_in_meters / self.depth_scale
        '''

        self.align_to   = rs.stream.color
        self.align      = rs.align(self.align_to)


    #update camera
    def get_frame(self, isRecording):
        #wait for frames from d435
        if(self.frame_num < 30):
            frames = self.pipeline.wait_for_frames()
            self.frame_num += 1
            return (0, 0)    
        frames          = self.pipeline.wait_for_frames()
        aligned_frames  = self.align.process(frames)
        depth_frame     = aligned_frames.get_depth_frame()
        color_frame     = aligned_frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image     = np.asanyarray(depth_frame.get_data())
        color_image     = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap  = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)

        #saves RGB and depth info to two different files
        if isRecording:
            self.color_out.write(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
            # self.depth_dict[self.frame_num] = depth_image[self.height/2, self.width/2]
            # self.write_depth_data(depth_image, self.frame_num)
            # self.depth_out.write(depth_colormap)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))

        # Update frame counter
        self.frame_num += 1
        return (1, images)

    #create new video writer object to write video frames
    def new_writer(self):
        self.color_out = cv2.VideoWriter(self.fileName + '.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))
        # self.depth_out = cv2.VideoWriter(self.fileName + 'depth_out.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height))

    def close_writer(self):
        self.color_out.release()
        # self.depth_out.release()
        self.write_depth_data()
        self.depth_dict.clear()

    def save(self):
        # This needs to be fixed
        self.fileName = tk.filedialog.asksaveasfilename(initialdir = full_path, title = "Save As",filetypes =[("Video files","*.avi")])
        
    def write_depth_data(self):
        for frame in self.depth_dict.keys():
            np.savetxt(full_path+"\\depth_out\\"+ str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+'_frame'+str(frame)+'.txt', self.depth_dict[frame], fmt='%i')
    #destructor
    def __del__(self):
        try:
            self.pipeline.stop()
        except:
            pass