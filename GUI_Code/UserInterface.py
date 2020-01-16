import tkinter as tk
import cv2
import time
import numpy as np
from VideoCapture import VideoCapture
from PIL import ImageTk, Image

class UserInterface:
    def __init__(self, window, title):


        self.sourceCam = 0

        #creating a window
        self.window = window 
        self.window.title(title)
        self.vid = VideoCapture(self.sourceCam)
        
        #sets up space for the video
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        
        #buttons
        self.capture_button = tk.Button(window, text="Begin Capture", command=self.begin_capture)
        self.capture_button.pack()
        self.stop_button = tk.Button(window, text="Stop Capture", state="disabled", command=self.stop_capture)
        self.stop_button.pack()
        
        #cannot run continuosly
        self.delay = .5
        self.update()

        self.window.mainloop()

    #start video recording
    def begin_capture(self):
        self.capture_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        print("Started here")

    #stop video recording
    #open up a prompt to name file to save to
    def stop_capture(self):
        self.capture_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        print("Stopped here")


    #Sends video frames to the gui, no slowdown so far
    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.imgtk, anchor=tk.NW)
        self.canvas.after(1, self.update)