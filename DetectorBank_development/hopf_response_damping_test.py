#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:54:02 2017

@author: keziah
"""


import numpy as np
from scipy.io.wavfile import read
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from time import time

from save_plot import SavePlot, SaveLegend

plt.style.use('thesis-small-fig')

def formatLabelFreq(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.3f} Hz'.format(label))
        
        
def formatLabelDamp(label):
    if label == 0:
        return '{0:.0f}'.format(label)
    else:
        return '{0:.0e}'.format(label)
        
        
def get_b(bandwidth, amplitude):

    y0, y1 = 0.15, 20
    x0, x1 = 2, 10
    
    m = (np.log(y1) - np.log(y0)) / (np.log(x1) - np.log(x0))
    logb = m * np.log(abs(bandwidth)) - m * np.log(x0) + np.log(y0)
    b25 = -np.exp(logb)
    b = 625 * b25 / amplitude**2

    return b

sp = SavePlot(False, 'damping_gain_amp_unnorm.pdf')
sl = SaveLegend('damping_gain_amp_norm_legend.pdf')
    
method = DetectorBank.runge_kutta
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized

    
sr = 48000

f = np.array([100])

d = np.linspace(1e-4, 5e-4, 5)
gain = np.array([50, 25, 100, 10, 200])

d_s = ['{:.0e}'.format(dmp) for dmp in d]
g_s = [', {}'.format(g) for g in gain]
labels = [d_s[n]+g_s[n] for n in range(len(d_s))]

lineparam = [['red',5], ['orange',4], ['darkmagenta',3], ['lawngreen',2], 
              ['blue',1]]

pltparam = dict(zip(labels, lineparam))

b = np.zeros(len(f))
det_char = np.array(list(zip(f, b)))
#gain = 25

dur = 3
t = np.linspace(0, 2*np.pi*f[0]*dur, sr*dur)
audio = np.sin(t)
audio = np.append(audio, np.zeros(2*sr))

r = np.zeros((len(d),len(audio)))

# colour and zorder for each damping factor
#pltparam = {'1e-04':['red',5], '2e-04':['orange',4], '3e-04':['darkmagenta',3], 
#            '4e-04':['lawngreen',2], '5e-04':['blue',1]}

#pltparam = {'1e-04':['red',5], '2e-04':['orange',4], '3e-04':['darkmagenta',3], 
#            '4e-04':['lawngreen',2], '5e-04':['blue',1]}

for n in range(len(d)):
   
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d[n], gain[n])
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)    
    det.getZ(z)
    
    r0 = np.zeros(z.shape)
    m = det.absZ(r0, z)
    r[n] = r0



#c = list(reversed(['red', 'darkmagenta', 'blue', 'darkslategrey']))
#style = ['-', ':', '--', '-.']
#style = list(reversed(style))
     
t = np.linspace(0, len(audio)/sr, len(audio))


#subsample = False
#subFactor = 400
#
## SUBSAMPLE
#if subsample:
#    new_r = np.zeros((len(r), int(len(r[0])/subFactor)))
#    
#    for k in range(len(r)):
#        new_r[k] = r[k][::subFactor]
#    
#    t = np.linspace(0, len(audio)/sr, len(new_r[0]))
#    
#    for k in range(len(r)):
#        line, = plt.plot(t, new_r[k], 'black', label=d[k], linestyle=style[k])
#    
#        
#if not subsample:       
#    t = np.linspace(0, len(audio)/sr, len(audio))
#
#    for k in range(len(r)):
#        line, = plt.plot(t, r[k], 'black', label=d[k], linestyle=style[k])
        
        
        

for k in range(len(r)):
#    line, = plt.plot(t, r[k]/max(r[k]), c[k], label=d[k])
    damping = d[k]
    key = labels[k] #formatLabelDamp(damping)
    c, z = pltparam[key]
    line, = plt.plot(t, r[k], color=c, label=key, zorder=z)
    # rise time
#    plt.axvline(rstms[k][0]/sr, ymax=r[k][rstms[k][0]]/5, color=c[k],
#                linestyle='--')
#    plt.axvline(rstms[k][1]/sr, ymax=r[k][rstms[k][1]]/5, color=c[k],
#                linestyle='--')
    # relaxtion time
#    plt.axvline(rxtms[k][0]/sr, ymax=r[k][rxtms[k][0]]/5, color=c[k],
#                linestyle='--')
#    plt.axvline(rxtms[k][2]/sr, ymax=r[k][rxtms[k][2]]/5, color=c[k],
#                linestyle='--')


ax = plt.gca()

majorLocator = MultipleLocator(1)
minorLocator = MultipleLocator(0.5)
ax.xaxis.set_major_locator(majorLocator)
ax.xaxis.set_minor_locator(minorLocator)
ax.grid(True, 'both')

#ax.yaxis.labelpad = 10
    
#handles, labels = ax.get_legend_handles_labels()
#labels, handles = zip(*sorted(zip(map(float,labels), handles)))
#labels = map(formatLabelDamp, labels)
#plt.legend(handles, labels, bbox_to_anchor=(1.0, 1))

#plt.legend(title='Damping, Gain')

labels = list(pltparam.keys())
colours = [v[0] for v in pltparam.values()]

#sl.plot(labels, colours=colours, title='Damping, Gain')

plt.xlabel('Time (s)')
plt.ylabel('|z|', rotation='horizontal', labelpad=10)
sp.plot(plt)
#plt.show()
#plt.close()
