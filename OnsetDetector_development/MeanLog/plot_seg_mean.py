#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot segment means
"""

import numpy as np
from detectorbank import DetectorBank
from onsetdetector_temp import OnsetDetector
import matplotlib.pyplot as plt
import soundfile as sf
import os
import seaborn as sns

sns.set_style('whitegrid')


def make_band(f0, band_type, num):
    
    if band_type == '1Hz-spaced':
        hwidth = num//2
        step = 1
        f = np.arange(f0-hwidth, f0+hwidth+step, step)
        
    else:
        lwr = -(num-1)//2  # lower range bound for frequency calculation
        upr =  (num+1)//2  # upper range bound for frequency calculation
        f = np.array(list(f0*2**(k/(12*num)) for k in range(lwr,upr)))
        
    return f


fname = 'bfr48' # 'dre48' # 
file = os.path.join('..', 'data', fname + '.wav')
audio, sr = sf.read(file)
audio = audio[:int(sr*15)]

method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 50

if fname == 'dre48':
    k = -2
elif fname == 'bfr48':
    k = 1
    
f0 = 440*2**(k/12)

band_types = ['1Hz-spaced', 'EDO']
band_type = band_types[0]

num = 21

threshold = 0.04

f = make_band(f0, band_type, num)

bandwidth = np.zeros(len(f))
det_char = np.array(list(zip(f, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                   method|f_norm|a_norm, d, gain)

od = OnsetDetector(det)
avgs = []

while True:
    try:
        avg = od.getSegAvg()
        avgs.append(avg)
    except IndexError:
        break
    
avgs = np.array(avgs)

# find consecutively incresing segments
inc = []
count = 0
for n in range(1, len(avgs)):
    if avgs[n] >= avgs[n-1]:
        count += 1
    else:
        if count >= 3 and avgs[n] >= threshold:
            inc += list(range(n-count-1,n))
        count = 0
        
# change the range to zoom in on the area with several detections
for n in range(350, 400): # len(avgs)): #
    if n in inc:
        c = 'dodgerblue'
    else:
        c = 'red'
    plt.scatter(n, avgs[n], color=c, marker='.')
        
#x = np.arange(len(avgs))      
#plt.plot(x, avgs, color='red', linestyle='', marker='.')
plt.xlabel('Segment')
plt.ylabel('Mean |z|')#, rotation='vertical')
plt.grid(True)

#ytx = [0, 0.1, 0.2, 0.3, 0.4]
#plt.yticks(ytx)

plt.show()
plt.close()
    