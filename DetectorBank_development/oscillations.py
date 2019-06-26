#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the small oscialltions in a low frequency response by subtracting a 
response generated at a higher frequency, where the oscillations are less
pronounced.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns

import peakdetect as pk

sns.set_style('whitegrid')

responses = []
sr = 48000
dur = 2 #120 #2

freqs = [5, 400] # [5] # [950, 960] # 

for f0 in freqs:

    # make audio
    t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
    audio = np.sin(t)
    audio = np.append(audio, np.zeros(sr))
    
    # DetectorBank Parameters
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    d = 0.0001
    gain = 25
    f = np.array([f0])
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    
    # get response
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)
    r = np.zeros(z.shape)
    det.getZ(z)
    det.absZ(r, z)
    
    # put in list
    responses.append(r[0])
    
    # plot 5Hz response
    if f0 == 5:
        t = np.linspace(0, len(audio)/sr, len(audio))
        plt.plot(t, r[0], color='darkmagenta')
    
        
plt.ylabel('|z|', rotation='horizontal')
plt.xlabel('Time (s)')
plt.grid(True)

ax = plt.gca()
ax.yaxis.labelpad = 10
plt.tight_layout()
plt.show()
plt.close()
        
    
r = responses[0] - responses[1]

t = np.linspace(0, len(audio)/sr, len(audio))

delta = 0.025

maxima, _ = pk.peakdet(r, delta, t)
f_osc = np.zeros(len(maxima)-1)

for n in range(1, len(maxima)):
    T = maxima[n][0] - maxima[n-1][0]
    f_osc[n-1] = 1/T
    
mean = np.mean(f_osc)

T2 = (maxima[-1][0] - maxima[0][0]) / (len(maxima)-1)
f_osc2 = 1/T2


plt.plot(t, r, color='darkmagenta')
plt.ylabel('Difference')
plt.xlabel('Time (s)')
plt.grid(True)

ax = plt.gca()

plt.tight_layout()

#plt.scatter(*zip(*maxima), marker='+', linewidth=1, color='black', zorder=10)

plt.show()
plt.close()

print('Mean oscillation frequency: {:.3f}Hz'.format(mean))
print('Oscillation frequency as difference between first and last peak: {:.3f}Hz'
      .format(f_osc2))
