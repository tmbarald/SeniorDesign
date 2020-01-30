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

        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, 30)
        
        self.pipeline.start(self.config)

        # #getting the webcam
        # self.vid = cv2.VideoCapture(sourceCam)
        # if not self.vid.isOpened():
        #     raise ValueError("source is wrong", 0)

        # #resolution of the camera
        #self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        #self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # #sets canvas to max width and height of captured video
        # self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        # self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        # self.vid.set(cv2.CAP_PROP_FOURCC, 0x32595559)
        # #not sure if we need this to set fps
        # #self.vid.set(cv2.CAP_PROP_FPS, 15)

        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # #self.out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, self.fourcc, 30.0, (640,480))

    #update camera
    def get_frame(self, isRecording):
        #camera is running

        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))
        return (1, images)

        # if self.vid.isOpened():
        #     #grab current frame
        #     ret, frame = self.vid.read()
        #     if ret:
        #         if isRecording:
        #             self.out.write(frame)
        #         return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        #     else:
        #         raise ValueError("Video stream connection interrupted!", None)
        # else:
        #     return (ret, None)
    
    #create new video writer object to write video frames
    def new_writer(self):
       self.out = cv2.VideoWriter('output.avi', cv2.CAP_ANY, self.fourcc, 30.0, (640,480)) 

    def close_writer(self):
        self.out.release()

    #destructor
    def __del__(self):
        # if self.vid.isOpened():
        #     self.vid.release()
        self.pipeline.stop()
    