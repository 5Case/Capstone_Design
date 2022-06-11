import cv2
import numpy as np
from utils.tracker import Tracker
from rpnUtils.rpnUtil import load_net
from rpnUtils.run_SiamRPN import SiamRPN_init, SiamRPN_track
from rpnUtils.network import *

from os.path import realpath, dirname, join

class SiamRPN_selective_template(Tracker):

    def name(self):
        return 'SiamRPN_selective_template'

    def initialize(self, image, region):
        #net = eval('SiamRPN_MOT16')()
        #load_net('./cp/{}.pth'.format('SiamRPN_MOT16'), net)
        net = SiamRPNotb() # pretrained SiamRPNotb 용
        net.load_state_dict(torch.load(join(realpath(dirname(__file__)), 'SiamRPNOTB.model'))) # pretrained SiamRPNotb 용
        net.eval().cuda()
        target_pos, target_sz = np.array([region[0]+region[2]/2, region[1]+region[3]/2]), np.array([region[2], region[3]])
        self.state = SiamRPN_init(image, target_pos, target_sz, net) # pretrained SiamRPNotb 용
        #self.state = SiamRPN_init(image, target_pos, target_sz, net, 'SiamRPN_MOT16')


    def track(self, image):
        self.state = SiamRPN_track(self.state, image)
        target_pos = self.state['target_pos']
        target_sz = self.state['target_sz']

        return [target_pos[0]-target_sz[0]/2, target_pos[1]-target_sz[1]/2, target_sz[0], target_sz[1]]
