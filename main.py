#!/usr/bin/env python

# Example of programming UR robot with gripper

import urx
import math
from time import sleep
import UR10_Robot

VEL = 0.2
ACC = 0.2
RVEL = 0.5

rob = UR10_Robot(ip="172.31.1.3", ACC, ACC, VEL, RVEL)

#Положительный y — к основанию
#положительный x — к машинам (влево от основания)
#z ok

if __name__ == "__main__":
    '''rob = urx.Robot("172.31.1.3")
    print("Connected to UR")
    rob.translate((-0.1, 0, 0), VEL, ACC)
    print('Current Pose', rob.get_pose())
    sleep(5)
    rob.translate((0, 0, -0.1), VEL, ACC)
    rob.movej((0, 0, 0, 0, 0, -3.14/2), RVEL, ACC, relative=True)
    print('Current Pose', rob.get_pose())
    sleep(5)
    rob.translate((0, 0, 0.2), VEL, ACC)
    print('Current Pose', rob.get_pose())
    sleep(5)
    rob.movej((0, 0, 0, 0, 0, 3.14/2), RVEL, ACC, relative=True)
    rob.close()'''
    sleep(0.5)
    rob.rtranslate(0.1, 0, 0)
    print(rob.get_pose())
    rob.gr_close()
    sleep(2)
    rob.rtranslate(-0.2, -0.1, 0.1)
    rob.gr_open()
    print(rob.get_pose())
    sleep(2)
    rob.rrotate(3.14/2)
    sleep(0.5)
    rob.rrotate(-3.14/2)
    sleep(0.5)
    rob.shutdown()
