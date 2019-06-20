#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Empirically determine at which point frequency shifting should automatically 
be applied.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot, SaveLegend
import os.path

import seaborn as sns
sns.set_style('whitegrid')
 
savepath = '/home/keziah/onsets/hsj/Visualisation/'
savefile = 'f_mod_rk4.pdf'
base, ext = os.path.splitext(savefile)
savelegend = base + '_legend' + ext

sp = SavePlot(False, os.path.join(savepath, savefile))
sl = SaveLegend(os.path.join(savepath, savelegend))

sr = 48000

f = np.array([1300, 1400, 1500, 1600, 1700, 1800])
#audio = np.zeros((len(f)+1)*sr)
audio = np.zeros(0)
dur = 4

for n in range(len(f)):
    t = np.linspace(0, 2*np.pi*f[n]*dur, sr*dur)
#    audio[n*sr:(n+1)*sr] = np.sin(t)
    audio = np.append(audio, np.sin(t))
audio = np.append(audio, np.zeros(sr))

if audio.dtype == 'int16':
    audio = audio / 2**15

# detectorbank  parameters
method = DetectorBank.runge_kutta# central_difference
f_norm = DetectorBank.freq_unnormalized# search_normalized #
a_norm = DetectorBank.amp_normalized
damping = 0.0001
# minimum bandwidth detectors
bandwidth = np.zeros(len(f))
det_char = np.column_stack((f, bandwidth))

#bandwidth[1] = 5
#bandwidth[2] = 7
#bandwidth.fill(5)
gain = 5

det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                   method|f_norm|a_norm, damping, gain)

z = np.zeros((len(f),len(audio)), dtype=np.complex128)  
det.getZ(z)

r = np.zeros(z.shape)
m = det.absZ(r, z)

#c = ['darkmagenta', 'red', 'blue', 'green']
c = ['red', 'darkorange', 'deeppink', 'darkmagenta', 'green', 'blue']#, 'blue']
labels = ['{} Hz'.format(freq) for freq in f]

t = np.linspace(0, r.shape[1]/sr, r.shape[1])
for k in range(r.shape[0]):
    line, = plt.plot(t, r[k], color=c[k], label=labels[k])
    
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
    
#plt.legend()
plt.grid(True)
#ax = plt.gca()
#ax.grid(True)


sp.plot(plt)


for k in range(r.shape[0]):
    samp = int(((k+0.5)*dur) * sr)
    print('{}Hz, Amplitude: {:.3f}'.format(f[k], r[k][samp]))


# making a legend with two rows (rather than four columns)
# need to re-order colours and labels so that the legend doesn't look weird

#idx = [0, 4, 1, 5, 2, 6, 3]
idx = [0, 3, 1, 4, 2, 5]
new_c = []
new_l = []
for i in idx:
    new_c.append(c[i])
    new_l.append(labels[i])

# figsize=(4.7, 0.5) for ncol=4
#sl.plot(new_l, colours=new_c, ncol=3, figsize=(3.6, 0.6), 
#        title='Detector frequencies')


