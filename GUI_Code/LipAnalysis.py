import cv2
from PIL import ImageTk, Image
import numpy as np
import pyrealsense2 as rs
from imutils import face_utils
import dlib
import imutils


vid = cv2.VideoCapture('color_out.avi')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


while vid.isOpened():
    ret, frame = vid.read()

    if frame is not None:
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 1)
        for(i, rect) in enumerate(rects):
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            for(name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
                if name == "mouth":
                    clone = frame.copy()
                    cv2.putText(clone, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    # loop over the subset of facial landmarks, drawing the
                    # specific face part
                    for (x, y) in shape[i:j]:
                        cv2.circle(clone, (x, y), 1, (0, 0, 255), -1)

                    # extract the ROI of the face region as a separate image
                        (x, y, w, h) = cv2.boundingRect(np.array([shape[i:j]]))
                        roi = frame[y:y + h, x:x + w]
                        roi = imutils.resize(roi, width=250, inter=cv2.INTER_CUBIC)

                    # show the particular face part
                        cv2.imshow("ROI", roi)
                        cv2.imshow("Image", clone)
                    #cv2.waitKey(0)

                    # visualize all facial landmarks with a transparent overlay
                #output = face_utils.visualize_facial_landmarks(frame, shape)
                #cv2.imshow("Image", output)




 #   cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or frame is None:
        break

vid.release()
cv2.destroyAllWindows()









