#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the mean log, including shaded areas and onsets
"""

import numpy as np
from detectorbank import DetectorBank, DetectorCache, Producer
import soundfile as sf
import matplotlib.pyplot as plt
import seaborn as sns
import os


def make_band(f0, band_type, num):
    """ Make array of critical band frequencies """
    
    if band_type == '1Hz-spaced':
        hwidth = num//2
        step = 1
        f = np.arange(f0-hwidth, f0+hwidth+step, step)
        
    else:
        lwr = -(num-1)//2  # lower range bound for frequency calculation
        upr =  (num+1)//2  # upper range bound for frequency calculation
        f = np.array(list(f0*2**(k/(12*num)) for k in range(lwr,upr)))
        
    return f


if __name__ == '__main__':
    
    sns.set_style('whitegrid')
    
    fname = 'dre48'
    file = os.path.join('..', 'data', fname + '.wav')
    audio, sr = sf.read(file)
    
    # these times correspond to different Figures
    # make sure to set the corresponding `onset_t` too!
    start_time = 13.185 # 13.125 # 4 #  0.06 # 10.5 # 8.5 #0 # 
    end_time = 13.285 # 13.3 #  4.4 # 0.16 # 13.285 # 12 # 9.1 #len(audio)/sr # 
    i0 = int(sr*start_time)
    i1 = int(sr*end_time)
    
    # time of onset to mark with dashed red line
    onset_t = 13.236 # 13.241 #  0.111 # 

    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    d = 0.0001
    gain = 50
    
    f0 = 440*2**(-2/12)
    
    # select and make critical band
    band_types = ['1Hz-spaced', 'EDO']
    band_type = band_types[1]
    num = 21 # 31 #
    f = make_band(f0, band_type, num)
    
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                       method|f_norm|a_norm, d, gain)
    
    chans = det.getChans()
    p = Producer(det)
    cache = DetectorCache(p, 2, sr//2)
    
    r = np.zeros(len(audio))
    for i in range(len(r)):
        for k in range(chans):
            r[i] += np.log(cache[k,i]) #cache[k,i] # 
        r[i] /= chans
    
    t = np.linspace(0, len(audio)/sr, len(audio))
    
    plt.plot(t[i0:i1], r[i0:i1])

    onset = int(onset_t * sr)
    plt.axvline(x=onset/sr, color='red', linestyle='--')
    
    # length 0.075 # of span (10ms or 75ms)
    span_t = 0.01 # 
    # for Fig 3.17a, span needs to end at 13.241
    onset = int(13.241*sr)
    spans = [(onset-int(span_t*sr), onset)]
    # alternatively, hard code span times (Fig 3.15)
#    spans = [(197760, 201600), (203520, 206400)]
    for span in spans:
        plt.axvspan(span[0]/sr, span[1]/sr, color='#d8d8d8', zorder=-1)
        
    plt.grid(True)
    plt.ylabel('Mean log')
    plt.xlabel('Time (s)')
    
    plt.show()
    plt.close()
        
