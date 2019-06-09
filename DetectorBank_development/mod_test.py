#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 11:52:47 2017

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank, FrequencyShifter
import matplotlib.pyplot as plt
import seaborn as sns

#plt.style.use('thesis-small-fig')
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
#f = np.arange(98, 103)

duration = 1
fin = 4000
t = np.linspace(0, 2*np.pi*fin*duration, sr*duration)
y = np.sin(t)
y = np.append(y, np.zeros(sr))
#y = np.append(np.zeros(sr), y)

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
#for k in range(r.shape[0]):
#    line, = plt.plot(t, r[k], 'black', linestyle=style[k], label=f[k])
    
    
# subsmaple and different linestyles etc was for monochrome figures for paper
subsample = False
subFactor = 50

# SUBSAMPLE
if subsample:
    new_r = np.zeros((len(r), int(len(r[0])/subFactor)))
    
    for k in range(len(r)):
        new_r[k] = r[k][::subFactor]
    
    t = np.linspace(0, len(y)/sr, len(new_r[0]))
    
    for k in range(len(r)):
        line, = plt.plot(t, new_r[k], 'black', label=f[k], linestyle=style[k])
    
        
if not subsample:       
    t = np.linspace(0, len(y)/sr, len(y))

    for k in range(len(r)):
#        if f[k] == 100:
#            label = '100 Hz'
#        else:
#            label = '100$\pm${:.1f} Hz'.format(abs(f[k]-100))
#        line, = plt.plot(t, r[k], 'black', label=label, linestyle=style[k-2])
        line, = plt.plot(t, r[k], color=c[k], label=f[k])


ax = plt.gca()
handles, labels = ax.get_legend_handles_labels()
labels, handles = zip(*sorted(zip(map(float,labels), handles)))
labels = map(formatLabel, labels)
plt.legend(handles, labels, title='Det. freq.') 
        
#plt.legend(title='Detector freq.')

ax = plt.gca()
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
ax.yaxis.labelpad = 10

plt.xticks(np.linspace(0, 2, 5))

#plt.legend()

plt.grid(True)
plt.show()
#
#plt.savefig('../Visualisation/ssb_modulation_hopf_output_rk_un_new.pdf', 
#            format='pdf')
plt.close()
#print('{}Hz'.format(f0))