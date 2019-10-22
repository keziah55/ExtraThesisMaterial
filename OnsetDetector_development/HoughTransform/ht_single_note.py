#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hough transform of single note
"""

import os.path
import numpy as np
from detectorbank import DetectorBank
import soundfile as sf
from hough import HoughTransformer
import plot_acc_surface as pa


def subsample(signal, factor):
    return signal[::factor]
    

fname = 'bfr48'
file = os.path.join('..', 'data', fname + '.wav')
audio, sr = sf.read(file)

method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 25

frequencies = np.array([440*2**(1/12)])
frequencies += 10 # approximate frequency of input
    
bandwidth = np.zeros(len(frequencies))
det_char = np.array(list(zip(frequencies, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                   method|f_norm|a_norm, d, gain)

buflen = det.getBuflen()

channels = det.getChans()

z = np.zeros((len(frequencies),len(audio)), dtype=np.complex128)
r = np.zeros(z.shape)
det.seek(0)
det.getZ(z)
m = det.absZ(r, z)

#for k in range(r.shape[0]):
t = np.linspace(0, len(audio)/sr, len(audio))
t0 = int(6*sr)
t1 = int(9*sr)
signal = r[-1][t0:t1]

# reduce number of points in signal
signal = subsample(signal, 100)

# get Hough transform and write the accumulator to a file
ht = HoughTransformer()
ht.transform(signal, q_steps=1000)
acc_csv = "hough.csv"
ht.write(acc_csv)

# load the HT accumulator
acc = np.loadtxt(acc_csv, delimiter=',')

# find max point
mx = np.where(acc==np.amax(acc))
t, r = [float(item[0]) for item in mx]
t, r = ht.unquantize(t, r)
print('Max at ({},{})=({:.3f},{:.3f})'.format('\u03C1', '\u03B8', t, r))

# plot params
r_max = acc.shape[1]/2
y = np.arange(0, np.pi, np.pi/180)
x = np.arange(-r_max, r_max, 1)

#pa.mpl(x, y, acc, projection='2D')
#pa.ply(x, y, acc)
