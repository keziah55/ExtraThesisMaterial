#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot frequency response curve from a whole DetectorBank driven by a 400Hz tone,
white noise or a tone in the presence of white noise at a signal-to-noise ratio
of either -4dB or -15dB.
"""

import numpy as np
import peakdetect as pk
import matplotlib.pyplot as plt
import seaborn as sns
import os.path

sns.set_style('whitegrid')

# Choose between DetectorBank response to tone, white noise, or both noise 
# and tone at SNR of -4dB or -15dB
modes = ['tone', 'noise', 'snr-4', 'snr-15']
mode = modes[0]

file = os.path.join('../Data', 'freqz_400_48000_5e-04_{}.csv'.format(mode))
arr = np.loadtxt(file, delimiter='\t', skiprows=1)

freq = arr[:,0]
mx = arr[:,1]

max_db = 20*np.log10(mx)

maxtab, _ = pk.peakdet(max_db, 15, freq)
peaks = maxtab[:,0]

for n in range(1, len(peaks)):
    diff = peaks[n]-peaks[n-1]
    data = (peaks[n-1], peaks[n], diff)
    print('Difference between {:9.3f} and {:9.3f}: {:8.3f} Hz'.format(*data))

plt.semilogx(freq, max_db, color='dodgerblue')

xtx = 2*np.logspace(0, 4, num=5)
xlab = ['{:g}'.format(x) for x in xtx]
plt.xticks(xtx, xlab)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Peak amplitude (dB)')
plt.grid(True, which='both')

plt.show()
plt.close()
