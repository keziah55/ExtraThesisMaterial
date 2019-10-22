#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manually fit two lines to the response of a note.
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import soundfile as sf
import os
import seaborn as sns

import ht_funcs as ht

sns.set_style('whitegrid')

fname = 'bfr48'
file = os.path.join('..', 'data', fname + '.wav')

audio, sr = sf.read(file)
audio = audio[:int(sr*15)]

method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 29

f0 = 440*2**(1/12)

hwidth = 10
step = 1
    
    
f = np.arange(f0-hwidth, f0+hwidth+step, step)

bandwidth = np.zeros(len(f))
det_char = np.array(list(zip(f, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                   method|f_norm|a_norm, d, gain)

buflen = det.getBuflen()

channels = det.getChans()

z = np.zeros((len(f),len(audio)), dtype=np.complex128)
r = np.zeros(z.shape)
det.seek(0)
det.getZ(z)
m = det.absZ(r, z)

######## matching straight line and decaying exponential

## get portion of response that corresponds to single note
#t = np.linspace(0, len(audio), len(audio))
t0 = 6*sr
t1 = int(9*sr)
#ts = t[t0:t1]
rs = r[-1][t0:t1]
ts = np.arange(len(rs))


rise_start = 8000
rise_end = 25000

## get equation for rise line
## rise is somewhere between 10000 and 25000
#rise_start = 10000
#rise_end = 25000
#
mx = np.max(rs)
mn = np.min(rs)
mxi = np.where(rs==mx)[0][0]
mni = np.where(rs==mn)[0][0]

mni = 12000
mn = rs[mni]

m = (mx-mn) / (mxi-mni)
c = -0.145 #-0.04 # -0.285 #-0.275 #-0.28 #found through trial and error

theta_ideal,rho_ideal = ht.m_c_to_theta_rho(m, c)

print('theta: {:.3f}, rho: {:.3f}'.format(theta_ideal, rho_ideal))

x0 = np.arange(mni, mxi)
y0 = m*x0 +c 

#
### get equation for relaxation decaying exponential
x1 = np.arange(mxi, len(rs))
y1 = 0.41*np.exp(-2*x1/sr)
#x1 = np.arange(35000, len(rs)) / sr
#y1 = np.exp(-2*x1)
#
### plot lines
ts = np.linspace(6, 9, len(rs))
plt.plot(ts, rs, 'darkmagenta', label='response')#, marker='o', linestyle='')
mark = ''
line = '--'
plt.plot(6+x0/sr, y0, 'lime', label='$y_0=mx_0+c$', 
         marker=mark, linestyle=line)
plt.plot(6+x1/sr, y1, 'cyan', label='$y_1=e^{-x_1}$', 
         marker=mark, linestyle=line)
##
#plt.axvline(6+mni/sr)

plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
plt.grid(True)

ax = plt.gca()
ax.yaxis.labelpad = 10

plt.show()
plt.close()
