import urx
import math
from time import sleep
from get_coords import get_cube_coords
import cv2
import imutils
import numpy as np
from imutils.video import VideoStream
from get_coords import get_cube_coords
from objects.Object import Bucket, Cube, Object
from Objects_detector import ObjectsDetector

H0 = 0.2793680869198448
COFF = 0.07
HG = 0.4250093061523666
SH = 0.7134657041263184

X0 = 299
Y0 = 387

W = 320
H = 180

class UR10_Robot:

    def __init__(self, ip, ac, rac, vel, rvel, gr_state=True):
        '''Initialization, connecting to UR10'''
        self.rob = urx.Robot(ip)
        print("Connected to UR")
        sleep(0.2)
        pp = self.rob.get_pose()
        print(pp)
        self.ac = ac
        self.rac = rac
        self.vel = vel
        self.rvel = rvel
        self.npose = self.rob.getl()
        self.gr_state = gr_state
        self.vs = VideoStream(src=0).start()
        sleep(0.5)

    def get_gripper_state(self):
        '''Getter for gripper state'''
        return self.gr_state

    def calc_transform_coef(self):
        '''Get pixels in 1 cm'''
        h = self.get_pose()
        h = h[2]
        return -1100000/9991*h + 938212/9991

    def rtranslate(self, x, y, z):
        '''relative translation'''
        self.rob.translate((x, y, z), self.vel, self.ac)
    
    def translate(self, pose):
        '''Global translation'''
        self.rob.translate(pose, self.vel, self.ac)

    def rrotate(self, phi):
        '''Relative rotation of end-effector'''
        self.rob.movej((0, 0, 0, 0, 0, phi), self.rvel, self.rac, relative=True)

    def rotate(self, phi):
        '''Global rotation of end-effector'''
        self.rob.movej((0, 0, 0, 0, 0, phi), self.rvel, self.rac)

    def gr_close(self):
        '''Close gripper'''
        header = "def myProg():\n"
        end = "end\n"
        prog = header # first put header into program code 
        prog += 'set_tool_digital_out(0, True)\n'
        prog += 'set_tool_digital_out(1, False)\n'
        prog += 'sleep(0.7)\n'
        prog += end
        self.rob.send_program(prog)
        print('sended')
        self.gr_state = not self.gr_state
        sleep(0.5)

    def gr_open(self):
        '''Open gripper'''
        header = "def myProg():\n"
        end = "end\n"
        prog = header # first put header into program code 
        prog += 'set_tool_digital_out(0, False)\n'
        prog += 'set_tool_digital_out(1, True)\n'
        prog += 'sleep(0.7)\n'
        prog += end
        print('sended')
        self.rob.send_program(prog)
        self.gr_state = not self.gr_state
        sleep(0.5)

    def get_pose(self):
        '''Get end-effector pose'''
        return self.rob.getl()

    def shutdown(self):
        '''Shutdown robot'''
        self.rob.close()
        print('Robot closed')
        cv2.destroyAllWindows()

    def release_object(self):
        '''Releasing obj'''
        coords = self.get_pose()
        h = coords[2]
        dh = H0 - h
        self.rtranslate(0, 0, dh)
        sleep(0.5)
        self.gr_open()
        sleep(0.5)
        self.rtranslate(0, 0, -dh)

    def take_object(self):
        '''Take obj from ground'''
        coords = self.get_pose()
        h = coords[2]
        dh = H0 - h
        self.rtranslate(0, 0, dh)
        sleep(0.5)
        self.gr_close()
        sleep(0.5)
        self.rtranslate(0, 0, -dh)

    def get_on_alt(self, H):
        '''Getting on global altitude'''
        coords = self.get_pose()
        h = coords[2]
        dh = H - h
        self.rtranslate(0, 0, dh)

    def take_cube(self, mask):
        '''Taking cube from fix alt'''
        self.get_on_alt(HG)
        detector = ObjectsDetector(debug_mode=True)
        frame = self.vs.read()
        objects = self.apply_mask(detector.get_objects(frame), mask)
        if len(objects) == 0:
            print('No obj')
            return
        coords = objects.get_position()
        dx = X0 - coords[0]
        dy = -(Y0 - coords[1])
        pic = 0.7*self.calc_transform_coef()
        print(dx, dy)
        self.rtranslate(dx/(100*pic), dy/(100*pic), 0)

    def get_bucket_coord(self, objects, mask):
        '''Getting bucket coordinates'''
        for obj in objects:
            if obj.get_color() == mask and obj.__class__.__name__ == "Bucket":
                return obj

    def apply_mask(self, objects, mask):
        '''Applying mask on objects'''
        for obj in objects:
            if obj.get_color() == mask and obj.__class__.__name__ == "Cube":
                return obj

    def get_down_center(self, mask):
        '''going down with focusing on object'''
        #TEST
        self.get_on_alt(SH)
        detector = ObjectsDetector(debug_mode=True)
        Np = 1
        coords = self.get_pose()
        h = coords[2]
        dh = (HG - h)/Np
        frame = self.vs.read()
        objects = self.apply_mask(detector.get_objects(frame), mask)
        if len(objects) == 0:
            print('No obj')
            return
        coords = objects.get_position()
        print(h)
        for i in range(Np):
            try:
                frame = self.vs.read()
                objects = self.apply_mask(detector.get_objects(frame), mask)
                coords = objects.get_position()
                print(get_cube_coords)
            except IndexError:
                print('Exception')
                pic = 0.7*self.calc_transform_coef()
                self.rtranslate(0, 0, dh)
                continue
            dx = W - coords[0]
            dy = -(H - coords[1])
            pic = 0.7*self.calc_transform_coef()
            print(pic)
            print('dxdy', dx/(100*pic), dy/(100*pic))
            self.rtranslate(dx/(100*pic), dy/(100*pic), dh)