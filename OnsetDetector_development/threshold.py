#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot response at different damping factors to see the effect on required 
threshold.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns
import soundfile as sf
import os

sns.set_style('whitegrid')

fname = 'dre48'

file = os.path.join('data', fname + '.wav')

audio, sr = sf.read(file)

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

plt.grid(True)
ax = plt.gca()
plt.xlabel('Time(s)')
ax.set_ylabel('|z|', labelpad=10, rotation='horizontal')
# plt.ylabel('|z|', rotation='horizontal')

#plt.xlim(ts0, ts1)
plt.yticks(np.linspace(0, 1.6, 9))

plt.show()
plt.close()
