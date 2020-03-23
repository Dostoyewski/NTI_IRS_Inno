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
import sys

NROB = 1

start_m_c = [0.11022135615486867, -0.5455495045770956, 0.7135153738252198]

H0 = 0.2793680869198448
#COFF = 0.09
#For r1
COFF = 0.07
HG = 0.4250093061523666
SH = 0.7134657041263184

X0 = 299
Y0 = 387

W = 640
H = 360

class NoObjException(Exception):
        print('No obj detected')

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
        self.TO = []
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

    def stab_xy(self, mask, typ):
        '''Taking cube from fix alt'''
        self.get_on_alt(HG)
        detector = ObjectsDetector(debug_mode=True)
        frame = self.vs.read()
        objects = self.apply_mask(detector.get_objects(frame), mask, typ)
        if objects is None:
            raise NoObjException('No obj')
        else:
            coords = objects.get_position()
            dx = X0 - coords[0]
            dy = -(Y0 - coords[1])
            pic = 0.7*self.calc_transform_coef()
            if NROB == 2:
                    pic = 0.6*self.calc_transform_coef()
                    if typ == 'Cube':
                        self.rtranslate(dx/(100*pic), dy/(100*pic) - 0.01, 0)
                    else:
                        self.rtranslate(dx/(100*pic) - 0.01, dy/(100*pic), 0)
            else:
                self.rtranslate(dx/(100*pic), dy/(100*pic), 0)

    def apply_mask(self, objects, mask, typ):
        '''Applying mask on objects'''
        for obj in objects:
            if obj.get_color() == mask and obj.__class__.__name__ == typ:
                return obj

    def get_down_center(self, mask, typ):
        '''going down with focusing on object'''
        #TEST
        self.get_on_alt(SH)
        detector = ObjectsDetector(debug_mode=True)
        Np = 1
        if typ == "Bucket":
            Np = 3
        coords = self.get_pose()
        h = coords[2]
        dh = (HG - h)/Np
        frame = self.vs.read()
        print(*detector.get_objects(frame))
        objects = self.apply_mask(detector.get_objects(frame), mask, typ)
        if objects is None:
            raise NoObjException('No obj')
        else:
            coords = objects.get_position()
            for i in range(Np):
                try:
                    frame = self.vs.read()
                    objects = self.apply_mask(detector.get_objects(frame), mask, typ)
                    coords = objects.get_position()
                except IndexError:
                    pic = 0.7*self.calc_transform_coef()
                    self.rtranslate(0, 0, dh)
                    continue
                dx = W - coords[0]
                dy = -(H - coords[1])
                pic = 0.7*self.calc_transform_coef()
                if NROB == 2:
                    pic = 0.6*self.calc_transform_coef()
                    if typ == 'Cube':
                        self.rtranslate(dx/(100*pic) + 0.005, dy/(100*pic) - 0.01, dh)
                    else:
                        self.rtranslate(dx/(100*pic) - 0.01, dy/(100*pic), dh)
                else:
                    self.rtranslate(dx/(100*pic), dy/(100*pic), dh)

    def check_existance(self, objects, objn):
        '''Checking existance in current map obj'''
        pos1 = objn.get_position()
        for i in range(len(objects)):
            pos = objects[i].get_position()
            if abs(pos[0] - pos1[0]) <= 0.05 and abs(pos[1] - pos1[1]) <= 0.05:
                #obj.set_position([(pos[0] + pos1[0])/2, (pos[1] + pos1[1])/2])
                if objn.__class__.__name__ == 'Bucket':
                    objects[i] = objn
                return True
        return False

    def make_map(self):
        '''Constructing map
        This function addes object to buil-in variable map'''
        self.get_on_alt(SH)
        detector = ObjectsDetector(debug_mode=True)
        frame = self.vs.read()
        objects = detector.get_objects(frame)
        print(*objects)
        for obj in objects:
            coords = obj.get_position()
            dx = W - coords[0]
            dy = -(H - coords[1])
            pic = 1.08*self.calc_transform_coef()*2
            bco = self.get_pose()
            dx /= 100*pic
            dy /= 100*pic
            if obj.__class__.__name__ == 'Bucket':
                a = Bucket([bco[0]+dx, bco[1]+dy], obj.get_color(), obj.get_radius())
            else:
                a = Cube([bco[0]+dx, bco[1]+dy], obj.get_color())
            if not self.check_existance(self.TO, a):
                print('Added new object')
                self.TO.append(a)

    def translate(self, x, y, z, zr=True):
        '''Moving in global Frame'''
        coord = self.get_pose()
        if not zr:
            self.rtranslate(x - coord[0], y - coord[1], z - coord[2])
        else:
            self.rtranslate(x - coord[0], y - coord[1], 0)

    def construct_map(self):
        '''Constructing map'''
        self.translate(0.11022135615486867, -0.5455495045770956, 0.7135153738252198, zr=False)
        self.make_map()
        self.rtranslate(0.5, 0, 0)
        N_points = 3
        for i in range(N_points):
            self.make_map()
            self.rtranslate(-1/N_points, 0, 0)
        self.rtranslate(0, -0.3, 0)
        for i in range(N_points):
            self.make_map()
            self.rtranslate(1/N_points), 0, 0)
        self.rtranslate(-0.5, 0, 0)

    def take_cube(self, cube):
        '''Takes cube object from ground,
        works with random altitude'''
        pos = cube.get_position()
        self.translate(pos[0], pos[1]+COFF, 0)
        self.gr_open()
        self.get_down_center(cube.get_color(), 'Cube')
        #Needs to calibrate hand angle
        self.stab_xy(cube.get_color(), 'Cube')
        self.take_object()
        print("object taked")

    def get_color_objects(self, color):
        '''Return array with objects, 
        sorted by type, color'''
        pos = self.get_pose()
        targets = []
        for obj in self.TO:
            obj.calc_distance(pos)
            if color == obj.get_color() and obj.__class__.__name__ == 'Cube':
                targets.append(obj)
        for obj in self.TO:
            if obj.__class__.__name__ == 'Bucket' and color == obj.get_color():
                targets.append(obj)
        return self.min_dist(targets)

    def min_dist(self, targets):
        '''This function are for calculating minimal distance'''
        last_bucket = targets[-1]
        targets.del[-1]
        targets.sorted(key = lambda x: x.distance)
        targets.append(last_bucket)
        return targets
     
    def take_all_cubes(self, color):
        '''This function takes all cubes on field'''
        obj = self.get_color_objects(color)
        bpos = obj[-1].get_position()
        count = len(obj) - 1
        for i in range(count):
            print('Taking cube')
            try:
                self.take_cube(obj[i])
            except NoObjException:
                print('No cube found on this coords', obj[i].get_position())
                continue
            self.translate(bpos[0], bpos[1]+COFF, 0)
            self.get_down_center(color, 'Bucket')
            self.stab_xy(color, 'Bucket')
            self.gr_open()
            sleep(0.5)