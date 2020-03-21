import urx
import math
from time import sleep

H0 = 0.2793680869198448

class UR10_Robot:

    def __init__(self, ip, ac, rac, vel, rvel, gr_state=True):
        '''Initialization, connecting to UR10'''
        self.rob = urx.Robot(ip)
        print("Connected to UR")
        sleep(0.2)
        self.ac = ac
        self.rac = rac
        self.vel = vel
        self.rvel = rvel
        self.npose = self.rob.getl()
        self.gr_state = gr_state

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
        self.gr_state = !self.gr_state
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
        self.gr_state = !self.gr_state
        sleep(0.5)

    def get_pose(self):
        '''Get end-effector pose'''
        return self.rob.getl()

    def shutdown(self):
        '''Shutdown robot'''
        self.rob.close()
        print('Robot closed')

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