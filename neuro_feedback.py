import sys, time, json, requests, math
from queue import Queue
from collections import Counter
import numpy as np

fatigue_update = {}

class NeuroFeedback(object):
    """Code to compute basic neurofeedback measures"""
    def __init__(self, windowSize, out_q):
        self.out_q = out_q
        self.windowSize = windowSize

        self.abs_spectrum_powers = {}
        self.abs_spectrum_powers['alpha'] = np.zeros((1, self.windowSize + 5))
        self.abs_spectrum_powers['delta'] = np.zeros((1, self.windowSize + 5))
        self.abs_spectrum_powers['beta'] = np.zeros((1, self.windowSize + 5))
        self.abs_spectrum_powers['theta'] = np.zeros((1, self.windowSize + 5))
        self.abs_spectrum_powers['acc'] = np.zeros((1, 200)) #Allocate longer buffer than necessary
       
        self.abs_spectrum_powers['gyro_x'] = np.zeros((1, 200)) #Allocate longer buffer than necessary
        self.abs_spectrum_powers['gyro_y'] = np.zeros((1, 200)) #Allocate longer buffer than necessary
        self.abs_spectrum_powers['gyro_z'] = np.zeros((1, 200)) #Allocate longer buffer than necessary
        self.abs_spectrum_powers['gyro_xyz'] = np.zeros((1, 200)) #Allocate longer buffer than necessary
        self.spectrum_ixs = Counter()
        self.spectrum_ixs['gyro_xyz'] = 0
        self.update_min = Counter()
        self.update_max = Counter()


    def abs_frequency_update(self, spectrum, value):
        self.abs_spectrum_powers[spectrum][0, self.spectrum_ixs[spectrum]] = value 
        self.spectrum_ixs[spectrum] += 1

        # Time lock to alpha frequency update
        if self.spectrum_ixs['alpha'] == self.windowSize:
            
            
            self.abs_spectrum_powers['gyro_xyz'] = np.sqrt( \
                np.power(self.abs_spectrum_powers['gyro_x'],2) + \
                np.power(self.abs_spectrum_powers['gyro_y'],2) + \
                np.power(self.abs_spectrum_powers['gyro_z'],2) \
            )
            
            self.abs_spectrum_powers['gyro_z'] = np.power(self.abs_spectrum_powers['gyro_z'],2)
            self.abs_spectrum_powers['gyro_y'] = np.power(self.abs_spectrum_powers['gyro_y'],2)

            power_updates = self.compute_power_updates()
      
            update = {}
            update['alpha-relaxation'] = power_updates['alpha'] 
            update['beta-concentration'] = power_updates['beta'] / power_updates['theta']
            update['theta-relaxation'] = power_updates['theta'] / power_updates['alpha']
            update['movement'] = power_updates['gyro_xyz']
            update['head-movement-horizontal'] = power_updates['gyro_z']
            update['head-movement-vertical'] = power_updates['gyro_y']

            update = self.standardize_updates(update)

            # Need to find min and max for normalization

            # if not self.update_min:
            #     self.update_min = Counter(update)

            # for key in update.keys():

            #     if update[key] < self.update_min[key]:
            #         self.update_min[key] = update[key]
            #     elif update[key] > self.update_max[key]:
            #         self.update_max[key] = update[key]
            
            # print self.update_min
            # print self.update_max

            self.out_q.put(update)


    def compute_power_updates(self):
        power_updates = {} 
        for key in self.spectrum_ixs.keys():
            power_updates[key] = np.sum(self.abs_spectrum_powers[key]) /\
                np.count_nonzero(self.abs_spectrum_powers[key])

            self.spectrum_ixs[key] = 0
            self.abs_spectrum_powers[key].fill(0)
        
        return power_updates

    def standardize_updates(self, update):
        update['head-movement-horizontal'] = (update['head-movement-horizontal'] - 13.98) / (8184.34 - 13.98)
        update['head-movement-vertical'] = (update['head-movement-vertical'] - 3.73) / (1064.59 - 3.73)
        update['movement'] = (update['movement'] - 4.08) / (72.94 - 4.08)
        update['beta-concentration'] = (update['beta-concentration'] + 12.25) / (16.85 + 12.25)
        update['theta-relaxation'] = (update['theta-relaxation'] + 4.53) / (1.68 + 4.53)
        update['alpha-relaxation'] = (update['theta-relaxation'] - 0.082) / (1.05 - 0.082)
        
        return update
    

    def async_update(self, updatetype):
        if updatetype == 'jaw_clench':
            update = {'jaw_clench' : 'true'}
        elif updatetype == 'blink':
            update = {'blink' : 'true'}
        
        self.out_q.put(update)

