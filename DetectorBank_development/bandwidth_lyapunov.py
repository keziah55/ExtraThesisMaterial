#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estimate value of first Lyapunov coefficient for a given bandwidth (frequency
difference).

This requires a version of DetectorBank which takes Lyapunov as an arg, 
rather than bandwidth.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt

def get_b(bandwidth):
    
    m = (np.log(532.883701808) - np.log(0.160401176805)) / (np.log(30) - 
         np.log(2))
    
    logb = m * (np.log(abs(bandwidth)) - np.log(2)) + np.log(0.160401176805)
    
    return -np.exp(logb)
    

def get_fd(damping):
    
    m = (4.58699193 - 1.15912846) / (0.0005 - 0.0001)
    
    bandwidth = m * damping + (m * -0.0005 + 4.58699193)
    
    return bandwidth


def make_input(f0, sr, dur):
    # mak sine tone
    t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
    audio = np.sin(t)
    audio = np.append(audio, np.zeros(sr))
    return audio
    

def getLyapunov(fd, f0, sr, plot=True, b=None):

    freq = np.array([f0-fd, f0, f0+fd])
    
    if b is None:
        b = get_b(2*fd)
    print('Frequency difference: {}Hz; Bandwidth: {}Hz'.format(fd,2*fd))
    print('First Lyapunov coefficient: {:.3f}'.format(b))
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    gain = 1
    damping = 0.0001
    dbp = (method|f_norm|a_norm, damping, gain)
    
    audio = make_input(f0, sr, 3)
    audio *= 25
    
    size = len(freq)
    bw = np.zeros(size)
    bw.fill(b)
    
    det_char = np.array(list(zip(freq, bw)))
    
    # NB have changed DetectorBank code to regard det_char as freq,fLc 
    # pairs instead of freq,bw pairs
    # all that is required to do this is change AbstractDetector::getLyapunov
    # to simply return the value it is passed
    # i.e. we pretend that 'bandwidth' values are Lyapunov coeff
    det = DetectorBank(sr, audio.astype(np.float32), 0, 
                       det_char, *dbp)
    
    # get output
    z = np.zeros((size,len(audio)), dtype=np.complex128)
    r = np.zeros(z.shape)
    det.getZ(z,size)
    det.absZ(r, z)
    
    t = np.linspace(0, r.shape[1]/sr, r.shape[1])
    c = ['blue', 'darkmagenta', 'red']
    
    mx_centre = np.max(r[np.where(freq==f0)[0][0]])
    
    maxima = np.array([np.max(k) for k in r])
    ratio = maxima/mx_centre
    ratio_db = 20*np.log10(ratio)
    
    for k in range(r.shape[0]):
        
        print('{:.0f}Hz; max = {:.4f}; ratio = {:.4f}; {:.4f}dB'.format(freq[k], 
              maxima[k], ratio[k], ratio_db[k]))
        
        if plot:
            line, = plt.plot(t, r[k], c[k])
            
    mean = (ratio_db[0]+ratio_db[2])/2
    diff = abs(-3 - mean)
    print('Mean ampltiude: {:.4f}dB'.format(mean))
    print('Difference from -3dB: {:.4f}dB'.format(diff))
        
    if plot:
        plt.show()
        plt.close()
    
    
    
if __name__ == '__main__':
    
#    fds = np.arange(1,6)
    fd = 5
#    for fd in fds:
    getLyapunov(fd, f0=440, sr=192000, plot=False, b=-20.43)
    print()
        
    
    