import numpy as np
import cv2 as cv
import os.path

cap = cv.VideoCapture(1, cv.CAP_ANY)
frame_count = 0
frame_dir = os.getcwd() + "\\frame_dir"
os.makedirs(frame_dir, exist_ok=True)

# with open(frame_dir+'\\somefile.txt', 'w+') as the_file:
#    the_file.write('Hello\n')

# Define the codec and create VideoWriter object
fourcc = cv.VideoWriter_fourcc(*'XVID')
out = cv.VideoWriter('output.avi', cv.CAP_ANY, fourcc, 60.0, (640, 480))
print(out.getBackendName())
print(cap.getBackendName())

while (cap.isOpened() & out.isOpened()):
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # frame = cv.flip(frame, 0)
    # write the flipped frame
    out.write(frame)

    #save frame by frame
    cv.imwrite(frame_dir+"\\frame%d.jpg" %frame_count, frame)
    frame_count += 1

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        print(frame_count)
        break

# Release everything if job is finished
cap.release()
out.release()
cv.destroyAllWindows()