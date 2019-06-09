#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 17:02:48 2017

@author: keziah
"""

import numpy as np
import detectorbank as db
import matplotlib.pyplot as plt

import os.path
import sys

f = np.array([440])
bw = np.zeros(len(f))
bw.fill(5)
det_char = np.array(list(zip(f, bw)))

d = 0.0001
#b = -200
method = db.DetectorBank.runge_kutta
f_norm = db.DetectorBank.freq_unnormalized
a_norm = db.DetectorBank.amp_unnormalized

sr = 48000

audio = np.zeros(0)

t = np.linspace(0, 2*np.pi*f[0], sr)
audio = np.append(audio, np.sin(t))
audio = np.append(audio, np.zeros(sr))

#lyapunovs = np.array([-1., -10., -100., -200., -400., -1000.])
colours = ['skyblue', 'blue', 'darkblue', 'lightslategrey', 'darkslategrey', 
           'black']

gains = np.array([0.01, 0.25, 0.6, 1.2, 2.5, 5, 10, 20, 40, 60, 80, 100])
#gains = np.linspace(0, 100, 101)
out_amp = np.zeros(len(gains))
    
#for n in range(len(lyapunovs)):
#    
#    b = lyapunovs[n]

for g in range(len(gains)):
    
    det = db.DetectorBank(sr, gains[g]*audio.astype(np.float32), 4, det_char, 
                          method|f_norm|a_norm, d)#, gains[g])
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)
    det.getZ(z)
    r = np.zeros(z.shape)
    m = det.absZ(r, z)
    
    out_amp[g] = m
        
#    plt.plot(gains, out_amp, '-.', color=colours[n], 
#             label=lyapunovs[n])
    
    
plt.plot(gains, out_amp, color='blue', label='System output')

x = np.linspace(0, 100)
y = (out_amp[-1]/100**(1/3)) * x**(1/3)
plt.plot(x, y, 'orange', label=r'$y=x^{1/3}$')

ax = plt.gca()
ax.grid(True)

def abs_float(x):
    return abs(float(x))
    
handles, labels = ax.get_legend_handles_labels()
#labels, handles = zip(*sorted(zip(map(float,labels), handles), reverse=True))
#labels, handles = zip(sorted(map(float, labels), key=lambda x: abs(x)), handles)
#plt.legend(handles, labels)

plt.xlabel('Input amplitude')
plt.ylabel('Output amplitude')
plt.show()
#plt.savefig('../Visualisation/amp_nonlinear_cube_root.pdf', format='pdf')
plt.close()