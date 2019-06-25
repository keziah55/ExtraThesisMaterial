#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use GA to find relationship between first Lyapunov coefficient and bandwidth
at different amplitudes and dampings.
"""

from lyapunov_bandwidth_amplitude_ga import GA, write_summary
import os
import numpy as np


def getB(fd, amp):
    # function to make seed value
    
    m = (np.log(532.883701808) - np.log(0.160401176805)) / np.log(15)
    logb = m * np.log(abs(fd)) + np.log(0.160401176805)
    b = -np.exp(logb) / ((amp/25)**2)
    
    return b


if __name__ == '__main__':
    
    pwd = os.getcwd()
    root = os.path.join(pwd, 'GA_amplitudes_log_5e-4')
        
    summary_path = os.path.join(root, 'summaries')
    if not os.path.exists(summary_path):
        os.makedirs(summary_path)
    
    f0 = 440
    sr = 48000
    
    bestVals = {}

    # array amplitudes on which to run GA
    amplitudes = np.flipud(np.logspace(-2, 2, num=5))

    # array of damping factors on which to run the GA
    damping = np.linspace(1e-4, 5e-4, 5)
    
#    damping = [5e-4]
    
    # array of half-bandwidths on which to run the GA
#    frequencies = np.linspace(1, 49, num=25)
    # log-spaced frequencies so that ln(|b|) vs ln(B) can be plotted
    frequencies = np.logspace(0, 4, base=np.e, num=25)
    
#    frequencies = np.linspace(2.25, 2.5, num=26)
    
    for a in amplitudes:
        
        for d in damping:
            
            a_dir = '{0:.3g}'.format(a)
            d_dir = '{:.0e}'.format(d)
            
            path = os.path.join(root, a_dir, d_dir)
            if not os.path.exists(path):
                os.makedirs(path)
                
            bestVals = {}

            for fd in frequencies:
                
                out = ('Amplitude: {:.3g}, Damping: {:.0e}, Bandwidth: {:.0f}Hz'
                      .format(a,d,2*fd))
                print('*'*len(out) + '\n' + out)
                
                # estimate first Lyapunov coefficient
                seed = getB(fd, a)
                
                fname = 'lyapunov_{:.2f}Hz.txt'.format(fd)
                resultspath = os.path.join(path, fname)
                
                ga = GA(resultspath, f0, sr, 2*fd, d, a, seed, seedvar=1, 
                        term=0.02)
                
                bestInd, fitness, ret, msg = ga.evolve()
                bestVals[fd] = (bestInd[0], fitness)
                
                status = 'Evolution complete\n'
                status += 'Amplitude: {0:.3g}, '.format(a)
                status += 'Damping: {:.0e}, '.format(d)
                status += 'Bandwidth: {:.0f}Hz\n'.format(2*fd)
                status += msg
                
#                notify.send(status)
#                print(status)
#                print()
                
        
            fname = '{:.3g}_{:.0e}_lyapunov.csv'.format(a, d)
            outpath = os.path.join(summary_path, fname)
            
            header = 'Bandwidth/2 (Hz),First Lyapunov coefficient,Error (dB),\n'
            write_summary(bestVals, outpath, header) 
