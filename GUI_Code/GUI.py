import tkinter as tk
import os
import sys
import cv2
from PIL import ImageTk, Image
import time
import numpy as np
from capture import VideoCapture

class UserInterface:
    def __init__(self, window, title):
        self.window = window
        self.window.title(title)
        self.vid = VideoCapture()
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        self.capture_button = tk.Button(window, text="Begin Capture", command=self.begin_capture)
        self.capture_button.pack()
        self.stop_button = tk.Button(window, text="Stop Capture", state="disabled", command=self.stop_capture)
        self.stop_button.pack()
        self.delay = 1
        self.update()

        self.window.mainloop()

    def begin_capture(self):
        self.capture_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        print("Started here")

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



master = UserInterface(tk.Tk(), "Minecraft")
