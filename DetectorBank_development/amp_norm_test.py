#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:54:02 2017

@author: keziah
"""


import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from save_plot import SavePlot


def formatLabelFreq(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.3f} Hz'.format(label))
        
        
def formatLabelDamp(label):
    if label == 0:
        return '{0:.0f}'.format(label)
    else:
        return '{0:.0e}'.format(label)
        
        
def get_b(bandwidth, amplitude):

    y0, y1 = 0.15, 20
    x0, x1 = 2, 10
    
    m = (np.log(y1) - np.log(y0)) / (np.log(x1) - np.log(x0))
    logb = m * np.log(abs(bandwidth)) - m * np.log(x0) + np.log(y0)
    b25 = -np.exp(logb)
    b = 625 * b25 / amplitude**2

    return b

sp = SavePlot(False)
    
method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized # change between normalized and unnormalized
    
sr = 48000

f = np.array([100])

d = np.linspace(1e-4, 5e-4, 5)
gain = np.array([50, 25, 100, 10, 200])

d_s = ['{:.0e}'.format(dmp) for dmp in d]
g_s = [', {}'.format(g) for g in gain]
labels = [d_s[n]+g_s[n] for n in range(len(d_s))]

lineparam = [['red',5], ['orange',4], ['darkmagenta',3], ['lawngreen',2], 
              ['blue',1]]

pltparam = dict(zip(labels, lineparam))

b = np.zeros(len(f))
det_char = np.array(list(zip(f, b)))

dur = 3
t = np.linspace(0, 2*np.pi*f[0]*dur, sr*dur)
audio = np.sin(t)
audio = np.append(audio, np.zeros(2*sr))

r = np.zeros((len(d),len(audio)))

for n in range(len(d)):
   
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d[n], gain[n])
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)    
    det.getZ(z)
    
    r0 = np.zeros(z.shape)
    m = det.absZ(r0, z)
    r[n] = r0



t = np.linspace(0, len(audio)/sr, len(audio))

for k in range(len(r)):
    damping = d[k]
    key = labels[k] 
    c, z = pltparam[key]
    line, = plt.plot(t, r[k], color=c, label=key, zorder=z)


ax = plt.gca()

majorLocator = MultipleLocator(1)
minorLocator = MultipleLocator(0.5)
ax.xaxis.set_major_locator(majorLocator)
ax.xaxis.set_minor_locator(minorLocator)
ax.grid(True, 'both')


labels = list(pltparam.keys())
colours = [v[0] for v in pltparam.values()]

plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal', labelpad=10)
sp.plot(plt)
