#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test frequency shifting
"""

import numpy as np
from detectorbank import DetectorBank, FrequencyShifter
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')

def formatLabel(label):
    return('{:.0f} Hz'.format(label))

def formatLabelFreqDiff(label):
    if label == f[0]:
        return('{:.0f} Hz'.format(label))
    else:
        return('{}$\pm${:.1f} Hz'.format(f[0], abs(f[0]-label)))

sr = 48000
f = np.array([90, 95, 100, 105, 110])

duration = 1
fin = 4000
t = np.linspace(0, 2*np.pi*fin*duration, sr*duration)
y = np.sin(t)
y = np.append(y, np.zeros(sr))

y = y.astype(np.float32)


mthd = DetectorBank.runge_kutta
fnrm = DetectorBank.freq_unnormalized
anrm = DetectorBank.amp_normalized
d = 0.0001
bw = np.zeros(len(f))
det_char = np.array(list(zip(f, bw)))

ys = np.zeros(y.shape, dtype=np.dtype('float32'))
fsmode = FrequencyShifter.fft
fs = FrequencyShifter(y, sr, fsmode)
fs.shift(-3900, ys)

det = DetectorBank(sr, ys.astype(np.float32), 4, det_char, mthd|fnrm|anrm, d)

z = np.zeros((len(f),len(y)), dtype=np.complex128)   
n = det.getZ(z)

r = np.zeros(z.shape)  
m = det.absZ(r, z)


t = np.linspace(0, r.shape[1]/sr, r.shape[1])
#c = ['blue', 'red', 'green']
c = ['red', 'orange',  'darkmagenta', 'lawngreen', 'blue']
style = ['-.', ':', '-', '--', '--']
style = ['-', ':', '--']
        
t = np.linspace(0, len(y)/sr, len(y))

for k in range(len(r)):
    plt.plot(t, r[k], color=c[k], label=f[k])


ax = plt.gca()
handles, labels = ax.get_legend_handles_labels()
labels, handles = zip(*sorted(zip(map(float,labels), handles)))
labels = map(formatLabel, labels)
plt.legend(handles, labels, title='Det. freq.') 
        
ax = plt.gca()
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
ax.yaxis.labelpad = 10

plt.xticks(np.linspace(0, 2, 5))

plt.grid(True)
plt.show()
plt.close()
