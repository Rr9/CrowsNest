import cv2 as cv
import numpy as np
from collections import deque
from time import sleep
from time import strftime

CAMERA = 0
FRAME_RATES = [.8, .2]
PIXELS = 640*480
DETECT_PERCENT = .009
NO_MOTION_TIME_THRESH = 36
WRITE_FPS = 4.5
REC_AFTER = 10
QUEUE_LEN = REC_AFTER

def shoot(feed, greyScale=0):
    a, frame = feed.read()
    if a:
        if greyScale == 1:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # cv.imshow('1', frame)
    return frame

def difference(im1, im2):
    sub = cv.subtract(cv.cvtColor(im1, cv.COLOR_BGR2GRAY), cv.cvtColor(im2, cv.COLOR_BGR2GRAY))
    _, thresh = cv.threshold(sub, 10, 255, cv.THRESH_BINARY)
    return thresh

def detectMotion(img):
    white = cv.countNonZero(img)
    return white/PIXELS > DETECT_PERCENT

userGone = 1
motionDetected = 0
noMotion = 0
outputName = 'out'
outputNumber = 0

feed = cv.VideoCapture(CAMERA)
fourcc = cv.VideoWriter_fourcc(*'DIVX')
feedOut = cv.VideoWriter(outputName+str(outputNumber)+'.avi', fourcc, WRITE_FPS, (640,480))

loopd = 0
pic = deque(maxlen = QUEUE_LEN)

for i in range(QUEUE_LEN):
    pic.append(shoot(feed, 0))
    sleep(.1)

while userGone:

    pic.append(shoot(feed, 0))

    cv.imshow("first", pic[QUEUE_LEN-1])
    threshDiff = difference(pic[QUEUE_LEN-1], pic[QUEUE_LEN-2])
    cv.imshow("sub", threshDiff)

    if(detectMotion(threshDiff)):
        motionDetected = 1
    else:
        noMotion +=1
        if(noMotion > NO_MOTION_TIME_THRESH):
            motionDetected = 0
            noMotion = 0
    #print(motionDetected)

    if(motionDetected ==1):
        if not feedOut.isOpened():
            feedOut = cv.VideoWriter(outputName + str(outputNumber) + '.avi', fourcc, WRITE_FPS, (640, 480))
            outputNumber+=1

        cv.circle(pic[REC_AFTER-1], (20,20), 8, (0, 0, 200), -1)
        cv.putText(pic[REC_AFTER-1], 'REC', (30, 27), cv.FONT_HERSHEY_SIMPLEX, .7, (0, 0, 255), 1, cv.LINE_AA)
        cv.putText(pic[0], strftime("%d %b %Y %H:%M:%S"), (13, 50), cv.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 180), 1, cv.LINE_AA)

        feedOut.write(pic[0])
        sleep(FRAME_RATES[1])
    else:
        if feedOut.isOpened():
            feedOut.release()
        sleep(FRAME_RATES[0])

    if cv.waitKey(1) & 0xFF == ord('q'):
        userGone = 0


feedOut.release()
feed.release()
cv.destroyAllWindows();