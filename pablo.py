__author__ = 'jae'

import argparse
import cv2
import numpy as np
import ps_drone
import time
import os

def draw_detections(img, rects):
    for x, y, w, h in rects:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255, 0), 3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A pigeon will follow you now",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("width", metavar="W", type=int, help="width of the HOG window")
    parser.add_argument("height", metavar="H", type=int, help="height of the HOG window")
    parser.add_argument("feature", metavar="F", type=str, help="detecting vector file")
    parser.add_argument("-o", "--output", nargs="?", type=str, help="video output")

    args = parser.parse_args()

    detector = [float(line)
                for line in open(args.feature,"r")]
    winSize = (args.width, args.height)
    blockSize = (16,16)
    blockStride = (8,8)
    cellSize = (8,8)
    nbins = 9
    hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nbins)
    hog.setSVMDetector(np.array(detector, dtype=np.float32))

    drone = ps_drone.Drone()								# Start using drone
    drone.printBlue("Battery: ")

    drone.startup()											# Connects to drone and starts subprocesses
    drone.reset()											# Always good, at start

    while drone.getBattery()[0] == -1:	time.sleep(0.1)		# Waits until the drone has done its reset
    time.sleep(0.5)											# Give it some time to fully awake

    drone.printBlue("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1]))	# Gives a battery-status

    drone.trim()
    drone.mtrim()
    drone.stopOnComLoss = True

    while drone.getBattery()[0] == -1:
        time.sleep(0.1)
    print "Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])
    drone.useDemoMode(True)

    drone.setConfigAllID()
    drone.sdVideo()
    # drone.hdVideo()
    drone.videoFPS(30)
    drone.frontCam()
    drone.fastVideo()
    # CDC = drone.ConfigDataCount
    # while CDC == drone.ConfigDataCount:
    #     time.sleep(0.0001)
    drone.startVideo()

    while drone.VideoImage is None:
        time.sleep(0.1)

    drone.takeoff()
    while drone.NavData["demo"][0][2]:
        time.sleep(0.1) # Wait until drone is completely flying

    if not args.output is None:
        dir = os.path.join(args.output, str(int(time.time())))
        os.makedirs(dir)
        dir += os.sep
    last_move_time = time.time()
    while True:
        frame = drone.VideoImage
        if not frame is None:
            found, w = hog.detectMultiScale(frame)
            draw_detections(frame, found)
            cv2.imshow("Drone feed", frame)
            if last_move_time + .15 < time.time() and len(found) != 0:
                first_rect = found[0]
                x, y, w, h = first_rect
                x2 = x + x / 2
                y2 = y + y / 2

                f_h, f_w = frame.shape[:2]
                f_x2 = f_w / 2
                f_y2 = f_h / 2

                rotate = (x2-f_x2) / float(f_x2)
                lift = -1.0 * (y2-f_y2) / float(f_y2)
                lift = 0

                print "Rotate value: " + str(rotate)
                print "Lift value: " + str(lift)

                if abs(rotate) > abs(lift):
                    if rotate > 0:
                        drone.turnRight(abs(rotate))
                    else:
                        drone.turnLeft(abs(rotate))
                else:
                    if lift > 0:
                        drone.moveUp(abs(lift))
                    else:
                        drone.moveDown(abs(lift))

                last_move_time = time.time()
            else:
                if last_move_time + 1 > time.time():
                    print "Stopping..."
                    drone.stop()
            if not args.output is None:
                # Save the frame so FFMPEG can correctly encode.
                cv2.imwrite(dir+str(int(time.time()))+".png",
                            frame,
                            [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        if cv2.waitKey(1) == 27:
            break

    drone.land()
