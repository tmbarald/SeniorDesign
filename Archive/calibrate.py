# draws 3D axis on image calibrated image
def draw(img, corners, imgPts):
    import numpy as np
    import cv2 as cv

    corner = tuple(corners[0].ravel())
    img = cv.line(img, corner, tuple(imgPts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgPts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgPts[2].ravel()), (0, 0, 255), 5)
    return img

def calibrate():
    import numpy as np
    import cv2 as cv
    import os.path
    import glob

    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # get the image
    # frame_dir = os.getcwd() + "\\frame_dir\\checkerboard.jpg"
    imgs = glob.glob(os.getcwd() +"\\frame_dir\\checkerboards\\*.jpg")

    # prepare object points
    objP = np.zeros((8*6,3), np.float32)
    objP[:,:2] = np.mgrid[0:8, 0:6].T.reshape(-1,2)
    
    # prepare axis size
    axis = np.float32([[3,0,0], [0,3,0],[0,0,-3]]).reshape(-1,3)

    # Arrays to store object point and image points from all the images
    objPoints = [] # 3d points in real world space
    imgPoints = [] # 2d points in image plane

    # loop over all images of checkerboard
    for fname in imgs:
        # load image
        img = cv.imread(fname)

        # convert to grayscale
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chessboard corners
        retval, corners = cv.findChessboardCorners(img, (8,6), None)

        # If found, add object points, image points (after refining them)
        if retval:
            objPoints.append(objP)

            corners2 = cv.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
            imgPoints.append(corners2)

            # Draw and display the corners
            img = cv.drawChessboardCorners(img, (8,6), corners2, retval)
            cv.imshow('corners', img)

            cv.waitKey(100)

    cv.destroyAllWindows()

    retval, cameraMatrix, distCoeffs, rvecs, tvecs = cv.calibrateCamera(objPoints, imgPoints, gray.shape[::-1], None, None)


    print(cameraMatrix)
    print(distCoeffs)

    # load distorted image
    img = cv.imread(imgs[0])
    h, w =img.shape[:2]
    newCamMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, (w,h), 1, (w,h))

    # undistort (each) image
    dst = cv.undistort(img, cameraMatrix, distCoeffs, None, newCamMatrix)

    # crop
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    
    while True:
        cv.imshow('calibrated',dst)
        if cv.waitKey(1) == ord('q'):
            break


    mean_error = 0
    tot_error = 0
    for i in range(len(objPoints)):
        imgPoints2, _ = cv.projectPoints(objPoints[i], rvecs[i], tvecs[i], cameraMatrix, distCoeffs)
        error = cv.norm(imgPoints[i],imgPoints2, cv.NORM_L2)/len(imgPoints2)
        tot_error += error

    mean_error = tot_error / len(objPoints)
    print ("mean error: %5.5f" % mean_error)

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    retval, corners = cv.findChessboardCorners(gray, (8,6), None)

    if retval:
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        _, rvecs, tvecs, inliers = cv.solvePnPRansac(objP, corners2, cameraMatrix, distCoeffs)
        imgPoints, jac = cv.projectPoints(axis, rvecs, tvecs, cameraMatrix, distCoeffs)
        img = draw(img, corners2, imgPoints)
        cv.imshow('axis', img)
        k = cv.waitKey(0) & 0xff
        if k == 's':
            cv.imwrite('axis.png', img)


    cv.destroyAllWindows()


    # retval, corners = cv.findChessboardCorners(checkerboard, size)

    # while retval:

    #     checkerboard = cv.drawChessboardCorners(checkerboard, size, corners, retval)
    #     cv.imshow("checkerboard", checkerboard)
    #     cv.imwrite(frame_dir+"\\foundCheckerboardCorners.jpg", checkerboard)

    #     if cv.waitKey(1) == ord('q'):
    #         print(frame_count)
    #         break
    
calibrate()