#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use GA to find relationship between first Lyapunov coefficient and bandwidth

"""

from lyapunov_bandwidth_amplitude_ga import GA, write_summary
import os
import numpy as np

def getB(fd):
        ''' Guess first Lyapunov coefficient value for a frequency difference,
            fd, based on old calculation.
        '''
        m = (np.log(20) - np.log(0.15)) / np.log(5)
        logb = m * np.log(abs(fd)) + np.log(0.15)
        return -np.exp(logb)
    

if __name__ == '__main__':

    pwd = os.getcwd()
    path = os.path.join(pwd, 'GA_Lyapunov_bandwidth_log')
    if not os.path.exists(path):
        os.makedirs(path)
    
    f0 = 440
    sr = 48000
    
    bestVals = {}

    # array of half-bandwidths on which to run the GA
#    frequencies = np.linspace(1, 50)
    # log-spaced frequencies so that ln(|b|) vs ln(B) can be plotted
    frequencies = np.logspace(0, 4, base=np.e, num=50)

    for fd in frequencies:
        
        seed = getB(fd)
        
        fname = 'lyapunov_{:.2f}Hz.txt'.format(fd)
        resultspath = os.path.join(path, fname)
        
        # have set gain=1 in GA, so I think amp should be 25?
        ga = GA(resultspath, f0, sr, 2*fd, 0.0001, 25, seed, seedvar=0.5, 
                term=0.01)
        
        bestInd, fitness, ret, msg = ga.evolve()
        bestVals[fd] = (bestInd[0], fitness)

    header = 'Bandwidth/2 (Hz),First Lyapunov coefficient,Error (dB),\n'
    write_summary(bestVals, os.path.join(path, 'lyapunov.csv'), header) 

