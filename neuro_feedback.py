import sys, time, json, requests, math
from queue import Queue
from collections import Counter
import numpy as np

fatigue_update = {}

class NeuroFeedback(object):
    """Code to compute basic neurofeedback measures"""
    def __init__(self, bufferWindowSize, minMaxWindowSize,  out_q):
        self.out_q = out_q
        self.bufferWindowSize = bufferWindowSize
        self.minMaxWindowSize = minMaxWindowSize

        #Create buffer to average down high frequency updates that looks bufferWindowSize into the past
        keys = ['alpha', 'delta', 'beta', 'theta', 'acc', 'gyro_x', 'gyro_y', 'gyro_z', 'gyro_xyz']
        update_keys = ['alpha-relaxation', 'beta-concentration', 'theta-relaxation', 'movement', 'head-movement-vertical', 'head-movement-horizontal']

        self.abs_spectrum_powers = dict(zip(keys, [np.zeros(200) for i in range(len(keys))]))
        self.buffer_spectrum_ixs = dict(zip(keys, [0]*len(keys)))

        #Create buffer for rolling min-max storage that looks minMaxWindowSize into the past
        self.rolling_min_maxs = dict(zip(update_keys, [np.zeros(self.minMaxWindowSize) for i in range(len(keys))]))
        self.rolling_min_max_ixs = dict(zip(update_keys, [0]*len(keys)))


    def abs_frequency_update(self, spectrum, value):

        self.abs_spectrum_powers[spectrum][self.buffer_spectrum_ixs[spectrum]] = value 
        self.buffer_spectrum_ixs[spectrum] += 1

        # Time lock to alpha frequency update
        if self.buffer_spectrum_ixs['alpha'] == self.bufferWindowSize:
            
            # Take magnitudes for motion updates
            self.abs_spectrum_powers['gyro_xyz'] = np.sqrt( \
                np.power(self.abs_spectrum_powers['gyro_x'],2) + \
                np.power(self.abs_spectrum_powers['gyro_y'],2) + \
                np.power(self.abs_spectrum_powers['gyro_z'],2) \
            )
            
            self.abs_spectrum_powers['gyro_z'] = np.power(self.abs_spectrum_powers['gyro_z'],2)
            self.abs_spectrum_powers['gyro_y'] = np.power(self.abs_spectrum_powers['gyro_y'],2)

            power_updates = self.compute_power_updates()

            # Calculate computed metrics
            update = {}
            update['alpha-relaxation'] = power_updates['alpha'] 
            update['beta-concentration'] = power_updates['beta'] / power_updates['theta']
            update['theta-relaxation'] = power_updates['theta'] / power_updates['alpha']
            update['movement'] = power_updates['gyro_xyz']
            update['head-movement-horizontal'] = power_updates['gyro_z']
            update['head-movement-vertical'] = power_updates['gyro_y']

            #Update min max buffer with current value before standardizing
            for key in update.keys(): 
                self.rolling_min_maxs[key][self.rolling_min_max_ixs[key]] = update[key]
                newix = (self.rolling_min_max_ixs[key] + 1) % self.minMaxWindowSize
                self.rolling_min_max_ixs[key] = newix
                
            update = self.standardize_updates(update)

            self.out_q.put(update)

    def compute_power_updates(self):
        '''Take average over the cached buffer'''
        power_updates = {} 
        for key in self.buffer_spectrum_ixs.keys():
            power_updates[key] = np.sum(self.abs_spectrum_powers[key]) /\
                np.count_nonzero(self.abs_spectrum_powers[key])

            self.buffer_spectrum_ixs[key] = 0
            self.abs_spectrum_powers[key].fill(0)
        
        return power_updates

    def standardize_updates(self, update):
        '''Standardize update based on min-max standardization, 
        where the min and max are calculated dynamically based on recently seen values'''
        for key in update.keys():
            update[key] = (update[key] - np.min(self.rolling_min_maxs[key])) /\
                (np.max(self.rolling_min_maxs[key]) - np.min(self.rolling_min_maxs[key]))
        
        return update
    
    def async_update(self, updatetype):
        if updatetype == 'jaw_clench':
            update = {'jaw_clench' : 'true'}
        elif updatetype == 'blink':
            update = {'blink' : 'true'}
        
        self.out_q.put(update)

