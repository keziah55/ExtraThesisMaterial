#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 20:30:36 2018

@author: keziah
"""

import numpy as np
import peakdetect as pk
import matplotlib.pyplot as plt
from save_plot import SavePlot
import seaborn as sns
import os.path

#plt.style.use('thesis-small-fig')
sns.set_style('whitegrid')

path = '/home/keziah/onsets/hsj/Visualisation/freqz/Test21'
file = os.path.join(path, 'freqz_400_48000_5e-04.csv')

#path = '/home/keziah/onsets/hsj/Visualisation/monochrome_figures'
savefile = os.path.join(path, 'freqz_400_48000_5e-04.pdf')

sp = SavePlot(False, savefile)

arr = np.loadtxt(file, delimiter='\t', skiprows=1)

#end = 2223
freq = arr[:,0]#[:end]
mx = arr[:,1]#[:end]

max_db = 20*np.log10(mx)

#where = np.where(max_db>=-20)[0]
#print(freq[where])

maxtab, _ = pk.peakdet(max_db, 15, freq)
peaks = maxtab[:,0]

#remove = []
#
#for n in range(1, len(peaks)):
#    diff = peaks[n]-peaks[n-1]
##    data = (peaks[n-1], peaks[n], diff)
##    print('Difference between {:9.3f} and {:9.3f}: {:8.3f} Hz'.format(*data))
#    if diff < 50:
#        remove.append(n)
#remove = np.array(remove)
#
#peaks = np.delete(peaks, remove)
#
#
for n in range(1, len(peaks)):
    diff = peaks[n]-peaks[n-1]
    data = (peaks[n-1], peaks[n], diff)
    print('Difference between {:9.3f} and {:9.3f}: {:8.3f} Hz'.format(*data))


#sns.set_style('darkgrid')
    
plt.semilogx(freq, max_db, color='dodgerblue') # color='black')# 

#plt.semilogx(freq, max_db, linestyle='', marker='.', color='dodgerblue', 
#             zorder=-1)

#for peak in peaks:
#    plt.axvline(peak, linestyle='--', color='red', zorder=-5)

xtx = 2*np.logspace(0, 4, num=5)
xlab = ['{:g}'.format(x) for x in xtx]
plt.xticks(xtx, xlab)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Peak amplitude (dB)')
plt.grid(True, which='both')

sp.plot(plt)

#plt.show()
#plt.savefig(os.path.join(path, 'freqz_400_48000_5e-04_1.pdf'), format='pdf')
#plt.close()


