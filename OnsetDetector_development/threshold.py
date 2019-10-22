#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 15:16:25 2018

@author: keziah
"""


import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns
import soundfile as sf
import os
from save_plot import SavePlot

sns.set_style('whitegrid')

fname = 'dre48'

user = os.path.expanduser('~')
project = os.path.join(user, 'onsets', 'hsj')
savepath = os.path.join(project, 'Visualisation', 'onset_detection', 
                        'threshold_backtrack')

file = os.path.join(project, 'Data', fname + '.wav') #'Sufi_songs', 

audio, sr = sf.read(file)

# audio = audio[:int(sr*15)]

onsets = np.array([8.47467, 8.98133, 9.76])

which = 0

ts0 = 8.25  #0 # onsets[which] - 0.1
ts1 = 10.25 # len(audio)/sr  #onsets[which] + 0.1
t0 = int(ts0*sr)
t1 = int(ts1*sr)
audio = audio[t0:t1]

if audio.dtype == 'int16':
    audio = audio / 2**15

method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 50

threshold = 0.8 #  0.3 # 

f = np.array([440*2**(-2/12)])

savename = '391Hz_response_dream_d1e-4_0825_1025s_thr' #'{:.0f}Hz'.format(np.round(f0))
#savename = '391Hz_response_dream_d1e-4'

sp = SavePlot(False, os.path.join(savepath, savename+'.pdf'),
              mode='quiet')
# sl = SaveLegend(os.path.join(savepath, '{:.0f}Hz_legend.pdf'
#                              .format(np.round(f0))), mode='quiet')

bandwidth = np.zeros(len(f))
det_char = np.array(list(zip(f, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                   method|f_norm|a_norm, d, gain)

# buflen = det.getBuflen()
channels = det.getChans()

z = np.zeros((len(f),len(audio)), dtype=np.complex128)
r = np.zeros(z.shape)
det.seek(0)
det.getZ(z)
det.absZ(r, z)

#t = np.linspace(0, len(audio)/sr, len(audio))
t = np.linspace(ts0, ts1, len(audio))

plt.plot(t, r[0], color='darkmagenta', linewidth=1)

#plt.ylim(-0.1, 2.1) #(-0.01, 0.41)

print('Plotted |z|...')

plt.axhline(threshold, color='green', linestyle='dashed')


#plt.axvline(8.925, color='lime')
#plt.axvline(onsets[which], color='red', linestyle='--')

# sl.save(labels, colours=c, figsize=(3,3), ncol=2)
#
# print('Saved legend...')
#
# plt.title('{:.0f} to {:.0f}Hz, centre {:.0f}Hz'.format(np.round(f[0]),
#           np.round(f[-1]),
#           np.round(f0)))
plt.grid(True)
ax = plt.gca()
plt.xlabel('Time(s)')
ax.set_ylabel('|z|', labelpad=10, rotation='horizontal')
# plt.ylabel('|z|', rotation='horizontal')

#plt.xlim(ts0, ts1)
plt.yticks(np.linspace(0, 1.6, 9))

sp.plot(plt)

print('Saved plot')

#print('Threshold exceeded at:')
#for t in thr_exc:
#    print('    {:.3f} seconds'.format(t/sr))
