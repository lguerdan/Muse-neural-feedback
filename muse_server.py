from liblo import *

import sys 
import time
from queue import Queue
from neuro_feedback import NeuroFeedback
import math


class MuseServer(ServerThread):
    #listen for messages on port 5000
    def __init__(self, out_q):
        ServerThread.__init__(self, 5020)
        self.feedback_calculator = NeuroFeedback(20, 30, out_q)

    ## Below updates computed bandpowers for each frequency range
    @make_method('/muse/acc', 'fff')
    def acc_callback(self, path, args):
        acc_x, acc_y, acc_z = args
        mag_acc = math.sqrt(acc_x * acc_x + acc_y * acc_y + acc_z * acc_z)
        self.feedback_calculator.abs_frequency_update('acc', mag_acc)

    @make_method('/muse/gyro', 'fff')
    def gyro_callback(self, path, args):
        gyro_x, gyro_y, gyro_z = args
        self.feedback_calculator.abs_frequency_update('gyro_x', gyro_x)
        self.feedback_calculator.abs_frequency_update('gyro_y', gyro_y)
        self.feedback_calculator.abs_frequency_update('gyro_z', gyro_z)

    # alpha absolute
    @make_method('/muse/elements/alpha_absolute', 'f')
    def alpha_callback(self, path, args):
        self.feedback_calculator.abs_frequency_update('alpha', args[0])

    # delta absolute
    @make_method('/muse/elements/delta_absolute', 'f')
    def delta_callback(self, path, args):
        self.feedback_calculator.abs_frequency_update('delta', args[0])

    # beta absolute
    @make_method('/muse/elements/beta_absolute', 'f')
    def beta_callback(self, path, args):
        self.feedback_calculator.abs_frequency_update('beta', args[0])

    # theta absolute
    @make_method('/muse/elements/theta_absolute', 'f')
    def theta_callback(self, path, args):
        self.feedback_calculator.abs_frequency_update('theta', args[0])

    @make_method('/muse/elements/jaw_clench', 'i')
    def eeg_callback(self, path, args):
        print 'jaw_clench'
        self.feedback_calculator.async_update('jaw_clench')

    @make_method('/muse/elements/blink', 'i')
    def eeg_callback(self, path, args):
        
        self.feedback_calculator.async_update('blink')


    #handle unexpected messages
    # @make_method(None, None)
    # def fallback(self, path, args, types, src):
    #     print "Unknown message \
    #     \n\t Source: '%s' \
    #     \n\t Address: '%s' \
    #     \n\t Types: '%s ' \
    #     \n\t Payload: '%s'" \
    #     % (src.url, path, types, args)


# q = Queue()

# try:
#     server = MuseServer(q)
# except ServerError, err:
#     print str(err)
#     sys.exit()


# server.start()

if __name__ == "__main__":
    while 1:
        time.sleep(1)