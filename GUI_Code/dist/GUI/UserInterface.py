import tkinter.filedialog
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import webbrowser as wb
import os

import cv2
import numpy as np

from lib.VideoCapture import VideoCapture
from lib.LipAnalysis import LipAnalysis


class UserInterface:

    def __init__(self, window, title):
        ## Assume source cam is 0
        # Possible feature: Allow user to slect source from a list of available cameras
        # May not always been on 0        
        self.sourceCam    = 0
        self.isRecording  = False
        self.enable_video = True
        
        ## Try to set camera feed
        try:
            self.vid = VideoCapture(self.sourceCam)
        except RuntimeError:
            print("COULD NOT FIND CAMERA! -- Maybe check the connection?")

    
        ## Set camera alignment assistance
        self.overlay = cv2.imread('./assets/overlay2.png')
        self.alignOverlay = True

        ## Creating a window
        self.window = window 
        self.window.option_add('*tearOff', False)
        self.window.title(title)
        
        ## Add icon to the window 
        self.main_dir = os.getcwd()
        self.window.iconbitmap('./assets/Minecraft.ico')

        ##############################################
        #                   MENUS                    #
        ##############################################
        self.isSettingsOpen = False

        ## Main menu bar
        self.menu          = tk.Menu(self.window)           
        self.file_menu     = tk.Menu(self.menu)             # File sub menu child
        self.settings_menu = tk.Menu(self.menu)             # Settings sub menu child
        self.help_menu     = tk.Menu(self.menu)             # Help sub menu child
        
        ## Items for file submenu
        self.file_menu.add_command(label = 'New Video', command=self.new_video)
        self.file_menu.add_command(label = 'New Analysis', command=self.new_analysis)
        self.file_menu.add_command(label = 'Open Video', command=self.update_settings)
        self.file_menu.add_command(label = 'Open Anaylsis', command=self.update_settings)
        self.file_menu.add_command(label = 'Save As..', command=self.update_settings)
        self.file_menu.add_command(label = 'Exit', command=self.exit)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        ##  Items for the settings submenu
        self.settings_menu.add_command(label = 'Resolution', command=self.update_settings)
        self.settings_menu.add_command(label = 'FPS', command=self.update_settings)
        self.settings_menu.add_command(label = 'Video Extension', command=self.update_settings)
        self.settings_menu.add_command(label = 'Save Video Seperately', command=self.update_settings)
        self.menu.add_cascade(label='Settings', menu=self.settings_menu)
        
        ## Items for the help submenu
        self.help_menu.add_command(label = 'VVV Documentation', command= lambda:wb.open('https://github.com/tmbarald/SeniorDesign/wiki'))
        self.help_menu.add_command(label = 'VVV GitHub', command= lambda:wb.open('https://github.com/tmbarald/SeniorDesign'))
        self.help_menu.add_command(label = 'Python', command= lambda:wb.open('https://docs.python.org/3.7/'))
        self.help_menu.add_command(label = 'RealSenseSDK', command= lambda:wb.open('https://github.com/IntelRealSense/librealsense'))
        self.help_menu.add_command(label = 'OpenCV', command= lambda:wb.open('https://docs.opencv.org/3.4/d1/dfb/intro.html'))
        self.help_menu.add_command(label = 'About', command=lambda:wb.open('https://github.com/tmbarald/SeniorDesign/blob/master/README.md'))
        self.menu.add_cascade(label='Help', menu=self.help_menu)

        self.window.config(menu=self.menu)

        ##  Sets up space for the video
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

        ## Safe extit variable and protocol
        self.quit = False
        self.window.protocol("WM_DELTE_WINDOW", self.exit)

        ## Initialize canvas
        self.update()

        ## Start the main tkinter loop
        self.window.mainloop()
        
    ## Start video recording
    def begin_capture(self):
        ## Ensure the file dialog was a success
        ret = self.vid.save()
        if ret:
            ## Toggle Capability of Pressing Buttons
            self.capture_button["state"] = "disabled"
            self.stop_button   ["state"] = "normal"

            ## Create a new video writer object ad set control variable
            self.vid.new_writer()
            self.isRecording = True

    ## Stop video recording
    def stop_capture(self):

        ## Toggle Capability of Pressing Buttons
        self.capture_button["state"] = "normal"
        self.stop_button   ["state"] = "disabled"
        
        self.isRecording = False
        self.vid.close_writer()

    ## Sends video frames to the gui, no slowdown so far
    def update(self):
        # Clear all object on canvas before writing new ones
        if self.enable_video:
            # Attempt to get frames from the camera object
            try:    
                ret, frame = self.vid.get_frame(self.isRecording)
                self.canvas.delete("all")
                if ret:
                    # Add overlay if enabled
                    if self.alignOverlay:
                        frame = cv2.addWeighted(frame,1,self.overlay,1,0)
                    # Create the image window on the GUI, and update it
                    self.imgtk = ImageTk.PhotoImage(image=Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image=self.imgtk, anchor=tk.NW)
                if self.quit:
                    exit()
                else:
                    self.job_id = self.canvas.after((1000//self.vid.fps), self.update)
                
            # Catch errors
            except AttributeError:
                 print("NO VIDEO TO UPDATE")
        else:
            # Display the analysis video
            try:
                ret, frame, roi, plot = self.lip_analysis.analysis()
                self.canvas.delete("all")
                if ret:
                    # Create the image window on the GUI, and update it
                    self.frame = ImageTk.PhotoImage(image=Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image=self.frame, anchor=tk.NW)
                    self.roi = ImageTk.PhotoImage(image=Image.fromarray(roi))
                    self.canvas.create_image(500, 180, image=self.roi, anchor=tk.NW)
                    if plot is not None:
                        self.plot = ImageTk.PhotoImage(image=Image.fromarray(plot))
                        self.canvas.create_image(750, 0, image=self.plot, anchor=tk.NW)
                    if self.quit:
                        self.lip_analysis.vid.release()
                        exit()
                    else:
                        self.job_id = self.canvas.after(330, self.update)
                else:
                    self.lip_analysis.vid.release()
            # Catach any errors 
            except Exception as e:
                print("Unable to start analysis: ", e) 

    ## Overlay controls    
    def toggle_overlay(self):
        ## Button to toggle overlay
        if self.alignOverlay:
            self.alignOverlay = False
        else:
            self.alignOverlay = True
        
    def update_settings(self):
        ## Creates the settings sub-window
        # Nothing in the settings window, due to scope changes
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
        ## Close the settings window
        self.isSettingsOpen = False
        self.window.settings.destroy()

    def new_analysis(self):
        self.fileName = tk.filedialog.askopenfilename(initialdir = self.main_dir, title = "Please select a video to perform analysis on...  ",filetypes =[("Video files","*.avi")], multiple = False)
        # Trying to check for when user closes prompt or selects cancel
        # Doesn't work, not sure what tk.filedialog returns when this is the case
        if (self.fileName is not ()) and (self.fileName is not ''):        
            self.lip_analysis = LipAnalysis(self.fileName)
            self.enable_video = False
            self.update()
    
    def new_video(self):
        # Remove previous instances related to lip analysis
        if not self.enable_video:
            self.lip_analysis.vid.release()
        self.enable_video = True
        self.update()

    def safe_exit(self):
        self.quit = True
        self.window.after_cancel(self.job_id)

    def exit(self):
        # Cancel all future canvas updates
        self.window.destroy()


