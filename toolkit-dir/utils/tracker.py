import os
from timeit import default_timer as timer
from abc import abstractmethod, ABC
from xml.sax.handler import property_encoding

from utils.dataset import Dataset
from utils.utils import calculate_overlap, posPrediction
from utils.io_utils import save_regions, save_vector

from utils.run_SiamRPNtracker import SiamRPN_init, SiamRPN_track
from utils.trackerNetwork import *
from os.path import realpath, dirname, join
import numpy as np

class Tracker(ABC):
    
    def __init__(self):
        pass
    
    @abstractmethod
    def initialize(self, img, region: list):
        pass

    @abstractmethod
    def track(self, img):
        pass

    @abstractmethod
    def name(self):
        pass

    def evaluate(self, dataset: Dataset, results_dir: str):
        count = 0
        for sequence in dataset.sequences:
            if count != 40: #49 = singer1, 40 - nature.
                count += 1
                continue

            count += 1
            print('Evaluating on sequence:', sequence.name)

            sequence_results_dir = os.path.join(results_dir, sequence.name)
            if not os.path.exists(sequence_results_dir):
                os.mkdir(sequence_results_dir)

            results_path = os.path.join(sequence_results_dir, '%s_%03d.txt' % (sequence.name, 1))
            time_path = os.path.join(sequence_results_dir, '%s_%03d_time.txt' % (sequence.name, 1))

            if os.path.exists(results_path):
                continue

            init_frame = 0
            frame_index = 0

            results = sequence.length * [[0]]
            times = sequence.length * [0]
            
            prevScores = []
            prevFrames=[]
            
            while frame_index < sequence.length:
                #print(f'-----frame index: {frame_index}-----\n')
                img = sequence.read_frame(frame_index)

                if frame_index == init_frame:
                    
                    t_ = timer()
                    self.initialize(img, sequence.gt_region(frame_index))
                    times[frame_index] = timer() - t_
                    results[frame_index] = [1]
                    frame_index += 1

                    image = img.copy()
                    pos = self.state['target_pos']
                    size = self.state['target_sz']
                    box = [frame_index, pos[0]-size[0]/2, pos[1]-size[1]/2, size[0], size[1], image, 1]
                    prevFrames.append(box)
                    prevScores.append(1)
                    
                    # (0608이후): template 고정부분도 활용
                    net = SiamRPNotb()
                    net.load_state_dict(torch.load(join(realpath(dirname(__file__)), 'SiamRPNOTB.model')))
                    net.eval().cuda()
                    targ_pos, targ_sz = np.array([pos[0], pos[1]]), np.array([size[0], size[1]])
                    state = SiamRPN_init(image, targ_pos, targ_sz, net)
                    
                else:

                    t_ = timer()
                    prediction = self.track(img)
                    times[frame_index] = timer() - t_
                    if self.state['score'] > 0.65 or prevScores[0] > 0.75 or prevScores[1] > 0.75:
                        results[frame_index] = prediction
                        
                        #prevScore = self.state['score']

                        if len(prevScores) == 2:
                            del prevScores[0]
                            prevScores.append(self.state['score'])
                        else:
                            prevScores.append(self.state['score'])

                        image = img.copy()
                        score = self.state['score']
                        box = [frame_index, prediction[0], prediction[1], prediction[2], prediction[3], image, score]
                        if len(prevFrames) == 10:
                            del prevFrames[0]
                            prevFrames.append(box)
                        else:
                            prevFrames.append(box)
                        
                        # (0608이후): template 고정부분도 활용
                        state = SiamRPN_track(state, img)
                        if state['score'] > self.state['score']:
                            newPos = state['target_pos']
                            newSz = state['target_sz']
                            results[frame_index] = [newPos[0]-newSz[0]/2, newPos[1]-newSz[1]/2, newSz[0], newSz[1]]
                        
                        frame_index += 1
                    else:
                        #print('frame: ', frame_index, '\n')
                        max, max_loc = 0, 0
                        for i in range(len(prevFrames)):
                            if max < prevFrames[i][6]:
                                max = prevFrames[i][6]
                                max_loc = i
                        best = prevFrames[max_loc]

                        #prevScore = self.state['score']
                        if len(prevScores) == 2:
                            del prevScores[0]
                            prevScores.append(self.state['score'])
                        else:
                            prevScores.append(self.state['score'])

                        results[frame_index] = [best[1], best[2], best[3], best[4]]
                        t_ = timer()
                        self.initialize(best[5], results[frame_index])
                        times[frame_index] = timer() - t_
                        
                        last = prevFrames[len(prevFrames)-1]
                        self.state['target_pos'] = np.array([last[1]+last[3]/2, last[2]+last[4]/2])
                        self.state['target_sz'] = np.array([last[3], last[4]])
                        pos = self.state['target_pos']
                        size = self.state['target_sz']
                        results[frame_index] = [pos[0]-size[0]/2, pos[1]-size[1]/2, size[0], size[1]]
                        
                        # (0608이후): template 고정부분도 활용
                        self.state['score'] = prevFrames[len(prevFrames)-1][6]
                        state = SiamRPN_track(state, img)
                        if state['score'] > self.state['score']:
                            newPos = state['target_pos']
                            newSz = state['target_sz']
                            results[frame_index] = [newPos[0]-newSz[0]/2, newPos[1]-newSz[1]/2, newSz[0], newSz[1]]
                        frame_index += 1                 
                
                '''
                if frame_index == init_frame:
                    t_ = timer()
                    self.initialize(img, sequence.gt_region(frame_index))
                    times[frame_index] = timer() - t_
                    results[frame_index] = [1]
                    frame_index += 1 
                        
                else:
                    t_ = timer()
                    prediction = self.track(img)
                    times[frame_index] = timer() - t_
                    #print('score: ', self.state['score'], '\n')
                    
                    results[frame_index] = prediction
                    frame_index += 1
                '''
                
                
                '''
                if frame_index == init_frame:
                    
                    t_ = timer()
                    self.initialize(img, sequence.gt_region(frame_index))
                    times[frame_index] = timer() - t_
                    results[frame_index] = [1]
                    frame_index += 1

                else:

                    t_ = timer()
                    prediction = self.track(img)
                    #print(f' prediction: {prediction}\n')
                    #print(sequence.gt_region(frame_index), '\n')
                    #print(calculate_overlap(prediction, sequence.gt_region(frame_index)), '\n')
                    times[frame_index] = timer() - t_

                    if len(prediction) != 4:
                        print('Predicted region must be a list representing a bounding box in the format [x0, y0, width, height].')
                        exit(-1)

                    if calculate_overlap(prediction, sequence.gt_region(frame_index)) > 0:
                        results[frame_index] = prediction
                        frame_index += 1
                    else:
                        results[frame_index] = [2]
                        frame_index += 5
                        init_frame = frame_index
                '''
            save_regions(results, results_path)
            save_vector(times, time_path)
