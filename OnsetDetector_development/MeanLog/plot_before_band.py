#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot responses of critical band to sund melody
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import soundfile as sf
import os.path
import seaborn as sns

sns.set_style('whitegrid')

fname = 'bfr48'
file = os.path.join('..', 'data', fname + '.wav')

audio, sr = sf.read(file)

method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 50

# one critical band around 466Hz
f0 = 440 * 2**(1/12)
hwidth = 10
step = 1
f = np.arange(f0-hwidth, f0+hwidth+step, step)

bandwidth = np.zeros(len(f))
det_char = np.array(list(zip(f, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                   method|f_norm|a_norm, d, gain)

z = np.zeros((len(f),len(audio)), dtype=np.complex128)
r = np.zeros(z.shape)
det.getZ(z)
det.absZ(r, z)

channels = det.getChans()


t = np.linspace(0, len(audio)/sr, len(audio))

t0 = 0 # 10.5 # 
t1 = len(audio)/sr # 12 # 
ts0 = int(t0*sr)
ts1 = int(t1*sr)

# colours = ['purple', 'dodgerblue', 'firebrick']
c = ['black', 'blue', 'chocolate', 'cyan', 'darkmagenta', 'darkorange',
     'deeppink', 'dodgerblue', 'khaki', 'firebrick', 'green',
     'lightslategrey', 'aquamarine', 'magenta', 'mediumvioletred', 
     'orange', 'pink', 'red', 'skyblue', 'lightgrey', 'yellow']
for k in range(channels):
    plt.plot(t[ts0:ts1], r[k][ts0:ts1], label='{:.3f}'.format(f[k]), color=c[k])

plt.grid(True)
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal', labelpad=10)

plt.xlim(t0, t1)

plt.show()
plt.close()
