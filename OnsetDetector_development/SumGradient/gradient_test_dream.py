#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:49:27 2017

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank, DetectorCache, Producer
from preprocessor import PreprocessorOD as Preprocessor
from onsetdetector import OnsetDetector
import matplotlib.pyplot as plt
import itertools
import scipy.io.wavfile
import os
import seaborn as sns

sns.set_style('whitegrid')


fname = 'dre48'

file = os.path.join('data', fname + '.wav')

sr, audio = scipy.io.wavfile.read(file)

if audio.dtype == 'int16':
    audio = audio / 2**15

# zoom in at the missed onset time
#ts0 = 8.4
#ts1 = 10
#t0 = int(ts0*sr)
#t1 = int(ts1*sr)
#audio = audio[t0:t1]

#sr = 48000
#f0 = 440
#
#x = np.linspace(0, 2*np.pi*f0, sr)
#audio = np.sin(x)
#audio = np.append(audio, np.zeros(4800))


method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized
d = 0.0001
gain = 50

# one critical band around 440Hz
f0 = 440 * 2**(-2/12)
hwidth = 10
step = 1
f = np.arange(f0-hwidth, f0+hwidth+step, step)
#f = np.arange(f0-10, f0+3, 1)

#f = np.array([384.995, 385.995, 391.995])

bandwidth = np.zeros(len(f))
det_char = np.array(list(zip(f, bandwidth)))
det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
                   method|f_norm|a_norm, d, gain)
#z = np.zeros((len(f),len(audio)), dtype=np.complex128)
#r = np.zeros(z.shape)
#det.getZ(z)
#det.absZ(r, z)

p = Producer(det)
seg_len = sr//2
cache = DetectorCache(p, 2, seg_len)

channels = det.getChans()
N = 1000
prep = Preprocessor(cache, seg_len, np.arange(channels, dtype=np.int_), N)

#gradient = np.array([prep.getGradient(n) for n in range(det.getBuflen())])

od = OnsetDetector(prep, np.arange(channels, dtype=np.int_), sr)

gradient = np.array([od.do_stuff(n) for n in range(det.getBuflen())])

onsets = od.onsets
offsets = od.offsets


#det = DetectorBank(sr, audio.astype(np.float32), 4, det_char,
#                   method|f_norm|a_norm, d, gain)
z = np.zeros((len(f),len(audio)), dtype=np.complex128)
r = np.zeros(z.shape)
det.seek(0)
det.getZ(z)
det.absZ(r, z)


#plt.plot(gradient)
#sp.plot(plt)

t = np.linspace(0, len(audio)/sr, len(audio))

# colours = ['purple', 'dodgerblue', 'firebrick']
c = ['black', 'blue', 'chocolate', 'cyan', 'darkmagenta', 'darkorange',
     'deeppink', 'dodgerblue', 'khaki', 'firebrick', 'green',
     'lightslategrey', 'aquamarine', 'magenta', 'mediumvioletred', 
     'orange', 'pink', 'red', 'skyblue', 'lightgrey', 'yellow']
for k in range(channels):
    plt.plot(t, r[k], label='{:.3f}'.format(f[k]), color=c[k])

## x ticks when 'zooming in' on missed onset
#xtick_loc = np.linspace(0, ts1-ts0, 9)
#xtick_lab = np.linspace(ts0, ts1, 9)
#plt.xticks(xtick_loc, xtick_lab)

#
#plt.legend(bbox_to_anchor=(1, 1))
#plt.show()
#plt.close()


# plot increasing and decreasing gradient by colouring in background
# darkgrey background: increasing, lightgrey: decreasing
# use plt.axvspan to draw a span for each inc/dec section
colours = ['darkgrey', 'lightgrey']

# use an cycle iterator to toggle between increasing and decreasing colours
# inc_dec_iter will provide the index to the 'colours' list
# if the first gradient is negative, first span is decreasing, else increasing
if gradient[0] < 0:
    inc_dec_iter = itertools.cycle((1, 0))
else:
    inc_dec_iter = itertools.cycle((0, 1))

n = 1
while n < len(gradient):

    # x value for start of span
    xmin = n-1

    # end of current span when sign of gradient changes
    try:
        while np.sign(gradient[n]) == np.sign(gradient[n-1]):
            n += 1
    except IndexError:
        # at end of gradient array, draw span to end
        n -= 1

    # x value for end of span
    xmax = n

    # index for colour list
    which = next(inc_dec_iter)

    plt.axvspan(t[xmin], t[xmax], color=colours[which])

    n += 1


for on in onsets:
    plt.axvline(on/sr, color='lime')
# for off in offsets:
#     plt.axvline(off/sr, color='red')

### draw dashed red line at missed onset
missed = 8.98133 #- ts0
plt.axvline(missed, color='red', linestyle='--')

#handles, labels = ax.get_legend_handles_labels()
#ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1, 1))
#plt.legend(bbox_to_anchor=(1, 1))

plt.xlabel('Time(s)')
plt.ylabel('|z|', rotation='horizontal')
plt.xlim(0, len(audio)/sr)

plt.grid(False)

ax = plt.gca()
ax.yaxis.labelpad = 10

sp.plot(plt)

#plt.savefig(os.path.join(savepath, savename+'.pdf'), format='pdf')
#            , bbox_inches='tight')
#plt.show()
#plt.close()
