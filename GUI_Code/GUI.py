from tkinter import *
import os
import sys
import cv2
from PIL import ImageTk, Image

cap = cv2.VideoCapture(1)

def start():
    _, frame = cap.read()
   # cv2.imshow("frame", frame)
    image_feed = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    #cv2.imshow("image_feed", image_feed)
    img = Image.fromarray(image_feed)
  #  cv2.imshow("img", img)
    imgtk = ImageTk.PhotoImage(image=img)
    video_part.imgtk = imgtk
    video_part.configure(image=imgtk)
    video_part.after(1, start)
    print("hello boi")

#print("hello world")
master = Tk()
master.title("Minecraft")
master.geometry('700x400')
#frame = Frame(master)
#frame.pack()
canvas = Frame(master, bg="white")
#canvas.pack()
canvas.grid()
video_part = Label(canvas)
video_part.grid()
redbutton = Button(canvas, text = 'Capture', fg ='red', command=start)
redbutton.grid()
master.mainloop()



