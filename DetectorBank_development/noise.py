#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the DetectorBank when presented with a tone in the presence of white noise
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')

def rms(signal):
    return np.sqrt(np.mean(np.square(signal)))

def power(signal):
    return np.mean(np.square(signal))

def signal_to_noise(signal, noise):
    p_s = power(signal)
    p_n = power(noise)    
    return 10 * np.log10(p_s/p_n)
 

sr = 48000

# Make noise. Set noise_amp for the desired signal-to-noise ratio
# For SNR=-15, noise_amp=6.95; SNR=-4, noise_amp=1.95
noise_amp = 6.95 # 1.95 # 1 # 
noise = noise_amp * (2 * np.random.random(sr) - 1)

# make tone
f = np.array([440])
tone = np.zeros(sr)
t = np.linspace(0, 2*np.pi*f[0], sr)
tone += np.sin(t)

audio = noise + tone # change to audio=noise to exclude the tone

# audio in range -1 to 1
audio = audio/np.amax(audio)


# detectorbank  parameters
method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_normalized
damping = 0.0001
# minimum bandwidth detectors
bandwidth = np.zeros(len(f))
#bandwidth[1] = 5
#bandwidth[2] = 7
#bandwidth.fill(5)
det_char = np.array(list(zip(f, bandwidth)))
gain = 5
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                   method|f_norm|a_norm, damping, gain)

z = np.zeros((len(f),len(audio)), dtype=np.complex128)  
det.getZ(z)

r = np.zeros(z.shape)
m = det.absZ(r, z)

c = ['darkmagenta', 'red', 'blue', 'green']

t = np.linspace(0, r.shape[1]/sr, r.shape[1])
for k in range(r.shape[0]):
    line, = plt.plot(t, r[k], 'darkmagenta') 
    
ax = plt.gca()
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
#ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax.yaxis.labelpad = 10
ax.grid(True)
plt.show()
plt.close()

if noise_amp > 0: 
    snr = signal_to_noise(tone, noise)
    print('SNR: {} dB'.format(snr))
