#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file generates the figures found in Section 2.2.1 of the thesis, and 
represent the initial investigation into how the DetectorBank responds to
inputs across a range of frequencies, using both numerical methods and 
with and without frequency normalisation.

In order to reproduce the results found in the thesis, the DetectorBank source
must be altered to turn off amplitude scaling, frequency shifting and sample
rate limitations.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot, SaveLegend
import seaborn as sns
import os.path


def formatLabel(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.0f} Hz'.format(label))


def mix(f0, amp, sr=48000):
    
    audio = np.zeros(sr)
    
    for n in range(len(f0)):
        t = np.linspace(0, 2*np.pi*f0[n], sr)
        audio += np.sin(t)*amp[n]
        
    audio = np.append(audio, np.zeros(sr))
    
    return audio


def make_audio(f0, amp, sr=48000):
    
    audio = np.zeros(0)
    
    for n in range(len(f0)):
        t = np.linspace(0, 2*np.pi*f0[n], sr)
        audio = np.append(audio, np.sin(t)*amp[n])
    
    return audio


def getFrequencies(mode):
    if mode == 'a':
        f = np.array([440*2**k for k in range(-4,4)])
    elif mode == 'low':
        f = np.array([440*2**(k/12) for k in range(-48, -35)])
    elif mode == 'high':
        f = np.array([440*2**(k/12) for k in range(24, 41)])
    else:
        raise ValueError("'mode' must be 'a', 'low' or 'high'")
    return f


def getColours(mode):
    if mode == 'a':
        c = ['red', 'darkorange', 'deeppink', 'darkmagenta', 'green', 
             'skyblue', 'blue', 'darkslategrey']
    elif mode == 'low':
        c = ['black', 'red', 'firebrick', 'darkorange', 'deeppink',
             'darkmagenta', 'mediumvioletred', 'green', 'lime', 
             'darkslategrey', 'lightslategrey', 'skyblue', 'blue']
    elif mode == 'high':
        c = ['black', 'red', 'firebrick', 'darkorange', 'salmon', 'deeppink',
             'darkmagenta', 'mediumvioletred', 'indigo', 'olive', 'green', 
             'lime', 'darkslategrey', 'lightslategrey', 'skyblue', 'blue', 
             'darkblue']
    else:
        raise ValueError("'mode' must be 'a', 'low' or 'high'")
    return c
    

def getResponses(sr, mode, method, f_norm):
    """ Get DetectorBank responses
    
        Parameters
        ----------
        sr : int
            sample rate
        mode : {'a', 'low', 'high'}
            frequency range
        method : DetectorBank Feature
            DetectorBank numerical method
        f_norm : DetectorBank Feature
            DetectorBank frequency normalisaion
            
        Returns
        -------
        2D array of |z| values
    """
        
    f = getFrequencies(mode)

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


def plotResponses(sp, r, sr, mode, subsample=False, subFactor=None):
    """ Plot DetectorBank responses
    
        sp : SavePlot object
            initialised SavePlot object
        r : 2D array
            responses
        sr : int
            sample rate
        mode : {'a', 'low', 'high'}
            frequency range
        subSample : bool
            whether or not to subsample the responses before plotting
        subFactor : int or None
            factor by which to subsample
    """

    chans, size = r.shape
    
    c = getColours(mode)
    
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
    plt.grid(True)
    
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
    
    plt.style.use('thesis-small-fig')
    sns.set_style('whitegrid')
    
    savepath = '/home/keziah/onsets/hsj/Visualisation/freq_range_figs/'
    
    s_rates = [48000, 96000, 192000]
    methods = {'rk4' : DetectorBank.runge_kutta, 
               'cd' : DetectorBank.central_difference}
    f_norms = {'un' : DetectorBank.freq_unnormalized,
               'sn' : DetectorBank.search_normalized}
    
    modes = ['a', 'low', 'high']
    
    sizes = [(3,0.9), (2.15,1.5), (2.35,1.9)]
    
    legend_sizes = dict(zip(modes, sizes))
    
    subsample = True
    subFactor = 500
    
    for sr in s_rates:
        for mode in modes:
            for mKey in methods:
                for fKey in f_norms:
                    
                    method = methods[mKey]
                    f_norm = f_norms[fKey]
                
                    file = 'sine_{}_{:.0f}_{}_{}.pdf'.format(mode, sr/1000,
                                                             mKey, fKey)
                    savefile = os.path.join(savepath, file)
                    sp = SavePlot(False, savefile, auto_overwrite=True)
                    
                    r = getResponses(sr, mode, method, f_norm)
                    
                    if sr > 48000:
                        subsample = True
                        subFactor = 500
                    else:
                        subsample = False
                        subFactor = None
                    
                    plotResponses(sp, r, sr, mode, subsample=subsample,
                                  subFactor=subFactor)
                    
                
    for mode in modes:
        
        file = '{}_legend.pdf'.format(mode)
        savefile = os.path.join(savepath, file)
        sl = SaveLegend(savefile)
        
        f = getFrequencies(mode)
        if mode == 'low':
            labels = ['{:.2f} Hz'.format(freq) for freq in f]
        else:
            labels = [formatLabel(freq) for freq in f]
        c = getColours(mode)
        
        sl.plot(labels, colours=c, figsize=legend_sizes[mode], ncol=2,
                title="Detector frequencies")
