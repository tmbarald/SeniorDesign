import tkinter.filedialog
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import webbrowser as wb

import cv2
import numpy as np

from VideoCapture import VideoCapture


class UserInterface:

    def __init__(self, window, title):        
        self.sourceCam    = 0
        self.isRecording  = False
        
        try:
            self.vid = VideoCapture(self.sourceCam)
        except RuntimeError:
            print("COULD NOT FIND CAMERA! -- Maybe check the connection?")
            
        self.overlay = cv2.imread('../assets/overlay2.png')
        self.alignOverlay = True

        #creating a window
        self.window = window 
        self.window.option_add('*tearOff', False)
        self.window.title(title)
        
        self.window.iconbitmap('.\\icons.\\Minecraft.ico')

        ##############################################
        #                   MENUS                    #
        ##############################################
        self.isSettingsOpen = False

        # Main menu bar
        self.menu          = tk.Menu(self.window)           
        self.file_menu     = tk.Menu(self.menu)             #file sub menu child
        self.settings_menu = tk.Menu(self.menu)             #settings sub menu child
        self.help_menu     = tk.Menu(self.menu)             #help sub menu child
        
        # Items for file submenu
        self.file_menu.add_command(label = 'New Video', command=self.update_settings)
        self.file_menu.add_command(label = 'New Analysis', command=self.update_settings)
        self.file_menu.add_command(label = 'Open Video', command=self.update_settings)
        self.file_menu.add_command(label = 'Open Anaylsis', command=self.update_settings)
        self.file_menu.add_command(label = 'Save As..', command=self.update_settings)
        self.file_menu.add_command(label = 'Exit', command=self.window.destroy)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        # Items for the settings submenu
        self.settings_menu.add_command(label = 'Resolution', command=self.update_settings)
        self.settings_menu.add_command(label = 'FPS', command=self.update_settings)
        self.settings_menu.add_command(label = 'Video Extension', command=self.update_settings)
        self.settings_menu.add_command(label = 'Save Video Seperately', command=self.update_settings)
        self.menu.add_cascade(label='Settings', menu=self.settings_menu)
        
        # Items for the help submenu
        self.help_menu.add_command(label = 'VVV Documentation', command= lambda:wb.open('https://github.com/tmbarald/SeniorDesign/wiki'))
        self.help_menu.add_command(label = 'VVV GitHub', command= lambda:wb.open('https://github.com/tmbarald/SeniorDesign'))
        self.help_menu.add_command(label = 'Python', command= lambda:wb.open('https://docs.python.org/3.7/'))
        self.help_menu.add_command(label = 'RealSenseSDK', command= lambda:wb.open('https://github.com/IntelRealSense/librealsense'))
        self.help_menu.add_command(label = 'OpenCV', command= lambda:wb.open('https://docs.opencv.org/3.4/d1/dfb/intro.html'))
        self.help_menu.add_command(label = 'About', command=self.update_settings)
        self.menu.add_cascade(label='Help', menu=self.help_menu)

        self.window.config(menu=self.menu)

        # Sets up space for the video
        try:
            self.canvas = tk.Canvas(window, width=2*self.vid.width, height=self.vid.height)
        except AttributeError:
            print("NO VIDEO TO DISPLAY")
            self.canvas = tk.Canvas(self.window, width = 640, height = 480)
        self.canvas.grid(column = 0, row = 0, columnspan = 8, rowspan = 8)
        
        ##############################################
        #                  BUTTONS                   #
        ##############################################
        self.capture_button = tk.Button(window, text = "Begin Capture", command=self.begin_capture)
        self.capture_button.grid(column = 0, row = 8, sticky = "nsew")
        
        self.stop_button = tk.Button(window, text = "Stop Capture", state = "disabled", command = self.stop_capture)
        self.stop_button.grid(column = 1, row = 8, sticky = "nsew", padx = 1)
        
        self.toggle_overlay_button = tk.Button(window, text = "Toggle Overlay", command=self.toggle_overlay)
        self.toggle_overlay_button.grid(column = 7, row = 8, sticky = "nsew")

        # Cannot run continuously
        self.delay = .01
        self.update()

        self.window.mainloop()
        
    # Start video recording
    def begin_capture(self):
    
        # Toggle Capability of Pressing Buttons
        self.capture_button["state"] = "disabled"
        self.stop_button   ["state"] = "normal"
        
        self.vid.save()
        self.vid.new_writer()
        self.isRecording = True

    # Stop video recording
    def stop_capture(self):
    
        # Toggle Capability of Pressing Buttons
        self.capture_button["state"] = "normal"
        self.stop_button   ["state"] = "disabled"
        
        self.isRecording = False
        self.vid.close_writer()

    # Sends video frames to the gui, no slowdown so far
    def update(self):
        try:    
            ret, frame = self.vid.get_frame(self.isRecording)
            if ret:
                if self.alignOverlay:
                    frame = cv2.addWeighted(frame,1,self.overlay,1,0)

                self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.imgtk, anchor=tk.NW)
            self.canvas.after(1, self.update)
            
        except AttributeError:
            print("NO VIDEO TO UPDATE")
        
    def toggle_overlay(self):
        if self.alignOverlay:
            self.alignOverlay = False
        else:
            self.alignOverlay = True
        
    def update_settings(self):
        if self.isSettingsOpen:
            print('The settings wundow is already open!')
            return
        self.window.settings = tk.Tk()
        self.window.settings.title("Settings")
        self.window.settings.geometry('350x200')
        self.window.settings.protocol("WM_DELETE_WINDOW", self.close_settings_window)
        self.btn = tk.Button(self.window.settings, text = "Click me to close", command = self.close_settings_window)
        self.btn.grid(column=1, row=0)
        if not self.isSettingsOpen:
            self.isSettingsOpen = True
        
    def close_settings_window(self):
        self.isSettingsOpen = False
        self.window.settings.destroy()
