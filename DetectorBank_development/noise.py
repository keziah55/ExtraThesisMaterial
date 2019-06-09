#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 17:01:54 2017

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns
from save_plot import SavePlot

sns.set_style('whitegrid')

def rms(signal):
    return np.sqrt(np.mean(np.square(signal)))

def power(signal):
#    return np.square(rms(signal))
    return np.mean(np.square(signal))

def signal_to_noise(signal, noise):
    p_s = power(signal)
    p_n = power(noise)    
    return 10 * np.log10(p_s/p_n)
 
## read audio from file
## the sample rate should be 48000 or 44100
#sr, audio = scipy.io.wavfile.read('../Data/dre48.wav')

plt.style.use('thesis-small-fig')
savename = '../Visualisation/noise_and_tone_440Hz_snr-15dB.pdf'
#savename = '../Visualisation/noise.pdf'
sp = SavePlot(False, savename)

sr = 48000

# For SNR=-15: noise_amp=6.95, SNR=-4: noise_amp=1.95
noise_amp = 6.95 # 1.95 # 1 # 
noise = noise_amp * (2 * np.random.random(sr) - 1)
#freq = 392
#f = np.array([39, 400, 450, 600])
f = np.array([440])
tone = np.zeros(sr)
#for freq in f:
t = np.linspace(0, 2*np.pi*f[0], sr)
tone += np.sin(t)

audio = noise + tone 

audio = audio/np.amax(audio)

#print('audio.shape: ', audio.shape)

if audio.dtype == 'int16':
    audio = audio / 2**15


#f = np.array([f[0]])#, 400, 450, 600])
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
    line, = plt.plot(t, r[k], 'darkmagenta') # 'black')# c[k])
    
ax = plt.gca()
plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal')
#ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax.yaxis.labelpad = 10
ax.grid(True)
#plt.show()
#plt.title('SNR: {:.4f} dB'.format(snr))
sp.plot(plt)


if noise_amp > 0: 
    snr = signal_to_noise(tone, noise)
    print('SNR: {} dB'.format(snr))
