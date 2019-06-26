#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find how quickly off-centre freqencies are detected and calculate the 
Delta t Delta f product.

The uncertainty principle states that Delta t Delta f >= 0.5
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt


def make_audio(f0, amp, sr=48000):
    
    audio = np.zeros(0)
    
    for n in range(len(f0)):
        t = np.linspace(0, 2*np.pi*f0[n], sr)
        audio = np.append(audio, np.sin(t)*amp[n])
    
    return audio


def getResponses(sr, f, method, f_norm):
    """ Get DetectorBank responses
    
        Parameters
        ----------
        sr : int
            sample rate
        f : ndarray
            frequencies
        method : DetectorBank Feature
            DetectorBank numerical method
        f_norm : DetectorBank Feature
            DetectorBank frequency normalisaion
            
        Returns
        -------
        2D array of |z| values
    """
        
    audio = make_audio(f, np.ones(len(f)), sr)
    
    d = 0.0001
    gain = 5
    a_norm = DetectorBank.amp_unnormalized
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)  
    r = np.zeros(z.shape)
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
    
    det.getZ(z)
    det.absZ(r, z)
    
    return r


def plotResponses(r, sr, subsample=False, subFactor=None):
    """ Plot DetectorBank responses
    
        Parameters
        ----------
        r : 2D array
            responses
        sr : int
            sample rate
    """

    chans, size = r.shape
    
    c = ['black', 'red']
    
    t = np.linspace(0, size/sr, size)

    for k in range(chans):
        line, = plt.plot(t, r[k], c[k])
        
    ax = plt.gca()
    plt.grid(True)
    
    ax.yaxis.labelpad = 13
    plt.xlabel('Time (s)')
    plt.ylabel('|z|', rotation='horizontal')
    
    plt.show()
    plt.close()
    

if __name__ == '__main__':
    
    # can test at different sample rates
    srates = [48000]#, 96000, 192000]
    
    # fundamental frequencies of the two lowest notes on a piano
    freq = np.array([440*2**(k/12) for k in [-48, -47]])
    
    for sr in srates:
        r = getResponses(sr, freq, DetectorBank.runge_kutta, 
                         DetectorBank.freq_unnormalized)
        plotResponses(r, sr)
    
        # get time of max in first second
        idx = np.where(r[1]==np.max(r[1][:sr]))[0][0]
        
        time = idx/sr
        time_ms = time * 1000
        
        print('Fs={:.0f}kHz, off-centre frequency rejected in {:.0f}ms'
              .format(sr/1000, time_ms))
        print('\u0394t \u0394f = {:.3f}'.format(time * (freq[1]-freq[0])))
    