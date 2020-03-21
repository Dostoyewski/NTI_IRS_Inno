#!/usr/bin/env python

# Example of programming UR robot with gripper

import urx
import math
from time import sleep
import close_gripper_cmd

VEL = 0.2
ACC = 0.2
RVEL = 0.5

def calc_transform_coef(h):
    return -1100000/9991*h + 938212/9991

#rob.send_program(prog)
#Положительный y — к основанию
#положительный x — к машинам (влево от основания)
#z ok

if __name__ == "__main__":
    rob = urx.Robot("172.31.1.3")
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
    rob.close()