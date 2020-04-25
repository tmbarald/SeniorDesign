# Libraries for GUI
import tkinter.filedialog
import tkinter as tk

# Libraries for processing
import numpy as np
import cv2
from PIL import ImageTk, Image
import pyrealsense2 as rs

# Libraries for system operations
import os
import csv
import datetime

# Video class
class VideoCapture:
    def __init__(self,sourceCam):

        # Some default variables for video, camera settings, etc
        self.videoType  = 'XVID'
        self.width      = 640
        self.height     = 480

        # FPS is off on my video files (alex)
        self.fps            = 30
        self.fileName       = 'default'
        self.frame_num      = 1
        self.exposure_count = 0
        
        # Get the working directory, so that files can be saved in the correct location
        self.main_dir = os.getcwd()


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
        
        # Start the camera pipeline, tell the camera to start with the above settings
        self.profile    = self.pipeline.start(self.config)

        # Set the codec for the video writer
        self.fourcc         = cv2.VideoWriter_fourcc(*self.videoType)

        # Set the depth sensor to HIGH_ACCURACY (2)
        self.depth_sensor   = self.profile.get_device().first_depth_sensor()
        self.depth_sensor.set_option(rs.option.visual_preset, 2)

        '''
        # Used to get depth scale
        self.depth_scale = self.depth_sensor.get_depth_scale()
        print("Depth scale is: ", self.depth_scale)
        self.clipping_distance_in_meters = 1
        self.clipping_distance = self.clipping_distance_in_meters / self.depth_scale
        '''

        # Tell the backend to align the depth frames to the RGB frames
        self.align_to   = rs.stream.color
        self.align      = rs.align(self.align_to)

    # Update camera
    def get_frame(self, isRecording):
        # Wait for autoexposure to finish before saving frames
        if(self.exposure_count < 30):
            frames = self.pipeline.wait_for_frames()
            self.exposure_count += 1
            return (0, 0)
        # Wait for frames to be recieved    
        frames          = self.pipeline.wait_for_frames()
        # Align the frames and store each 
        aligned_frames  = self.align.process(frames)
        depth_frame     = aligned_frames.get_depth_frame()
        color_frame     = aligned_frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image     = np.asanyarray(depth_frame.get_data())
        color_image     = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap  = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)

        # Saves RGB video and depth info (in progress)
        if isRecording:
            self.color_out.write(cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB))
            f = os.path.join(self.depth_wd, 'frame' + str(self.frame_num))
            np.save(f, depth_image)
            self.frame_num += 1

        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))

        return (1, images)

    # Create new video writer object to write video frames
    def new_writer(self):
        self.color_out = cv2.VideoWriter(self.fileName + '.avi', cv2.CAP_ANY, self.fourcc, self.fps, (self.width,self.height), True)

    # Free up the video writer objects
    def close_writer(self):
        self.color_out.release()

    # Open fileDialog so user can select location and name for video file
    def save(self):
        self.fileName = tk.filedialog.asksaveasfilename(initialdir = self.main_dir, title = "Save As",filetypes =[("Video files","*.avi")])
        # I would like to put the video into its directory (alex)
        self.depth_wd = os.path.normpath(os.path.join(self.fileName, 'depth_out'))
        try:
            os.mkdir(self.fileName)
            os.mkdir(self.depth_wd)
            print('Project output folder created!')
        except FileExistsError:
            print('Project output folder already exists!') 


    # Destructor
    def __del__(self):
        try:
            # Tell the camera to power down
            self.pipeline.stop()
        except:
            pass