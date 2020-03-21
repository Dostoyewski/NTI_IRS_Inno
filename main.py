#!/usr/bin/env python

# Example of programming UR robot with gripper

import urx
import math
from time import sleep
from UR10_Robot import UR10_Robot

VEL = 0.2
ACC = 0.2
RVEL = 0.5

MIN = 200

DELTA = 7

rob = UR10_Robot("172.31.1.3", ACC, ACC, VEL, RVEL)

#Положительный y — к основанию
#положительный x — к машинам (влево от основания)
#z ok

if __name__ == "__main__":
    '''sleep(0.5)
    rob.rtranslate(0.1, 0, 0)'''
    rob.stay_xy()
    print(rob.get_pose())
    sleep(2)
    rob.take_object()
    #rob.release_object()
    '''rob.gr_close()
    sleep(2)
    rob.rtranslate(-0.2, -0.1, 0.1)
    rob.gr_open()
    print(rob.get_pose())
    sleep(2)
    rob.rrotate(3.14/2)
    sleep(0.5)
    rob.rrotate(-3.14/2)
    sleep(0.5)'''
    
    rob.shutdown()
