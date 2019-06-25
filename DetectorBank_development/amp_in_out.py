#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the output amplitude for a range of input amplitudes.
"""

import numpy as np
import detectorbank as db
import matplotlib.pyplot as plt


f = np.array([440])
bw = np.zeros(len(f))
bw.fill(5) # non-degenerate detectors
det_char = np.array(list(zip(f, bw)))

d = 0.0001
method = db.DetectorBank.runge_kutta
f_norm = db.DetectorBank.freq_unnormalized
a_norm = db.DetectorBank.amp_unnormalized

sr = 48000

audio = np.zeros(0)

t = np.linspace(0, 2*np.pi*f[0], sr)
audio = np.append(audio, np.sin(t))
audio = np.append(audio, np.zeros(sr))

colours = ['skyblue', 'blue', 'darkblue', 'lightslategrey', 'darkslategrey', 
           'black']

gains = np.array([0.01, 0.25, 0.6, 1.2, 2.5, 5, 10, 20, 40, 60, 80, 100])
out_amp = np.zeros(len(gains))

for g in range(len(gains)):
    
    det = db.DetectorBank(sr, gains[g]*audio.astype(np.float32), 4, det_char, 
                          method|f_norm|a_norm, d)
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)
    det.getZ(z)
    r = np.zeros(z.shape)
    m = det.absZ(r, z)
    
    out_amp[g] = m
        
    
plt.plot(gains, out_amp, color='blue', label='System output')

x = np.linspace(0, 100)
y = (out_amp[-1]/100**(1/3)) * x**(1/3)
plt.plot(x, y, 'orange', label=r'$y=x^{1/3}$')

ax = plt.gca()
ax.grid(True)

def abs_float(x):
    return abs(float(x))
    
handles, labels = ax.get_legend_handles_labels()

plt.xlabel('Input amplitude')
plt.ylabel('Output amplitude')
plt.show()
plt.close()