import cv2
import imutils
import numpy as np
from imutils.video import VideoStream
import time

vs = VideoStream(src=1).start()
time.sleep(0.5)
MIN = 200

DELTA = 7

def get_cube_coords():
    frame = vs.read()
    frame = imutils.resize(frame, width=640, height=360)

    if frame is None:
        return

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (19, 19), 0)
    gray = cv2.cvtColor(hsv, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, 1)
    thresh = cv2.bitwise_not(thresh)
    cv2.imshow("thresh", thresh)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = []
    circles_coords = []

    circles = cv2.HoughCircles(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.HOUGH_GRADIENT, 1.5, 20)
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
        circles_coords.append([x, y])

    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < MIN:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        if not circles_coords:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            center.append([int(x + w / 2), int(y + h / 2)])
        for circle in circles_coords:
            if max((np.array([x, y]) - np.array(circle))) > DELTA:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                center.append([int(x + w/2), int(y + h/2)])
        #print(center)
    cv2.imshow("result", frame)
    key = cv2.waitKey(1) & 0xFF
    return center