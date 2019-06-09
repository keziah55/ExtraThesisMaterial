#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 14:36:01 2019

@author: keziah
"""

import numpy as np
import matplotlib.pyplot as plt
from detectorbank import DetectorBank


def getResponse(tone_freq, det_freq, bw, sr):

    f = np.array([det_freq])
    
    dur = 3
    t = np.linspace(0, 2*np.pi*dur, sr*dur)
    audio = np.sin(t*tone_freq)
    audio = np.append(audio, np.zeros(sr))
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    d = 0.0001
    gain = 50
    
    bandwidth = np.zeros(len(f))
    bandwidth.fill(bw)
    det_char = np.array(list(zip(f, bandwidth)))
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)
    r = np.zeros(z.shape)
    det.getZ(z)
    det.absZ(r, z)
    
    return r[0]
    
    
sr = 48000

# get response of minimum bandwidth detector driven at centre freq
r0 = getResponse(440, 440, 0, sr)
# get responses of B=10Hz detector, driven 5Hz from centre
r1 = getResponse(440, 435, 10, sr)
r2 = getResponse(440, 445, 10, sr)

r = [r0,r1,r2]

t = np.linspace(0, len(r0)/sr, len(r0))

for k in range(len(r)):
    plt.plot(t, r[k])
    
plt.ylabel('|z|', rotation='horizontal')
plt.xlabel('Time (s)')
plt.grid()
plt.show()
plt.close()

max0 = np.max(r0)
max1 = np.max(r1)
max2 = np.max(r2)

db1 = 20*np.log10(max0/max1)
print('{:.3f} dB'.format(db1))

db2 = 20*np.log10(max0/max2)
print('{:.3f} dB'.format(db2))