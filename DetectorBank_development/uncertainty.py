#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:07:25 2019

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot, SaveLegend
import os.path


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


def plotResponses(sp, r, sr, subsample=False, subFactor=None):
    """ Plot DetectorBank responses
    
        sp : SavePlot object
            initialised SavePlot object
        r : 2D array
            responses
        sr : int
            sample rate
        subSample : bool
            whether or not to subsample the responses before plotting
        subFactor : int or None
            factor by which to subsample
    """

    chans, size = r.shape
    
    c = ['black', 'red']
    
    # SUBSAMPLE
    if subsample:
        new_r = np.zeros((chans, int(size/subFactor)))
        
        for k in range(chans):
            new_r[k] = r[k][::subFactor]
        
        t = np.linspace(0, size/sr, len(new_r[0]))
        
        for k in range(len(r)):
            line, = plt.plot(t, new_r[k], c[k])
        
            
    if not subsample:       
        t = np.linspace(0, size/sr, size)
    
        for k in range(chans):
            line, = plt.plot(t, r[k], c[k])
        
        
    ax = plt.gca()
    plt.grid()
    
#    ax.xaxis.set_major_locator(majorLocator)
#    ax.xaxis.set_minor_locator(minorLocator)
#    ax.grid(True, 'both')
    
#    handles, labels = ax.get_legend_handles_labels()
#    labels, handles = zip(*sorted(zip(map(float,labels), handles)))
#    labels = map(formatLabel, labels)
#    plt.legend(handles, labels, bbox_to_anchor=(1.3, 1))
    
    ax.yaxis.labelpad = 13
    plt.xlabel('Time (s)')
    plt.ylabel('|z|', rotation='horizontal')
    
    sp.plot(plt)


if __name__ == '__main__':
    
    srates = [48000, 96000, 192000]
    
    freq = np.array([440*2**(k/12) for k in [-48, -47]])
    
    
    for sr in srates:
        r = getResponses(sr, freq, DetectorBank.runge_kutta, 
                         DetectorBank.freq_unnormalized)
        sp = SavePlot(False)
        plotResponses(sp, r, sr)
    
        # get time of max in first second
        idx = np.where(r[1]==np.max(r[1][:sr]))[0][0]
        
        time = idx/sr
        time_ms = time * 1000
        
        print('Fs={:.0f}kHz, off-centre frequency rejected in {:.0f}ms'
              .format(sr/1000, time_ms))
        print('\u0394t \u0394f = {:.3f}'.format(time * (freq[1]-freq[0])))
    