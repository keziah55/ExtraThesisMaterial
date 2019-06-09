#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:06:21 2016

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import MultipleLocator
from save_plot import SavePlot


def formatLabel(label):
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
    
    
def mix(f0, amp):
    
    audio = np.zeros(sr)
    
    for n in range(len(f0)):
    
        t = np.linspace(0, 2*np.pi*f0[n], sr)
        
        audio += np.sin(t)*amp[n]
        
#    audio = np.append(np.zeros(sr), audio)
    audio = np.append(audio, np.zeros(2*sr))
    
    return audio
    

sp = SavePlot(False, savefile='damping_broken_axis_2.pdf')

method = DetectorBank.central_difference
f_norm = DetectorBank.freq_unnormalized
a_norm = DetectorBank.amp_unnormalized

if method == DetectorBank.runge_kutta:
    mthd = 'rk'
elif method == DetectorBank.central_difference:
    mthd = 'cd'
    
if f_norm == DetectorBank.freq_unnormalized:
    nrml = 'un'
elif f_norm == DetectorBank.search_normalized:
    nrml = 'sn'

    
sr = 48000
f0 = 440
f = np.array([100])
amplitudes = np.array([1])

d = [0.0003, 0.0002, 0.0001, 0]
#b = -0.
gain = 1.4

bw = np.zeros(len(f))
det_char = np.array(list(zip(f, bw)))

audio = mix(f, amplitudes)

#sr, audio = read(filepath + file + '.wav')

r = np.zeros((len(d),len(audio)))

for n in range(len(d)):
   
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)    
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d[n], gain)
    
    det.getZ(z)

    r0 = np.zeros(z.shape)
    
    m = det.absZ(r0, z)
    
    r[n] = r0


for k in range(len(r)-1):

    rxamp = max(r[k]) / np.e
    mxtm = np.where(r[k]==max(r[k]))[0][0]
    rxtm = np.where(r[k][mxtm:]<=rxamp)[0][0]
    print('Damping: {:.0e}; Relaxation Time: {:.4f}'.format(d[k], rxtm/sr))
    









#c = ['red', 'darkorange', 'darkmagenta', 'deeppink', 'green',  'blue']
#c = ['green', 'darkmagenta', 'blue']
c = ['blue', 'darkmagenta', 'red', 'green'] # ['black', 'black', 'black', 'black']
style = ['-', '-', '-', '-'] # ['--', ':', '-', '-.'] # 

majorLocator = MultipleLocator(1)
minorLocator = MultipleLocator(0.25)

#f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
#fig = plt.figure()

ax1_upr = 2.8
ax1_lwr = 2.6
ax2_upr = 1
ax2_lwr = 0 

space = 0.1

ax1_size = ax1_upr - (ax1_lwr-space)
ax2_size = ax2_upr+space - ax2_lwr

ratio = [ax1_size/ax2_size,1]
gs = gridspec.GridSpec(2, 1, height_ratios=ratio)
ax1 = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])      

#t = np.linspace(0, len(audio)/sr, len(audio))
#
#for k in range(len(r)):
#    line, = ax1.plot(t, r[k], 'black', label=d[k], linestyle=style[k])
#    line, = ax2.plot(t, r[k], 'black', label=d[k], linestyle=style[k])
    

subsample = False
subFactor = 400

# SUBSAMPLE
if subsample:
    new_r = np.zeros((len(r), int(len(r[0])/subFactor)))
    
    for k in range(len(r)):
        new_r[k] = r[k][::subFactor]
    
    t = np.linspace(0, len(audio)/sr, len(new_r[0]))
    
    for k in range(len(r)):
        line, = ax1.plot(t, new_r[k], c[k], label=d[k], linestyle=style[k])
        line, = ax2.plot(t, new_r[k], c[k], label=d[k], linestyle=style[k])
    
        
if not subsample:       
    t = np.linspace(0, len(audio)/sr, len(audio))

    for k in range(len(r)):
        line, = ax1.plot(t, r[k], c[k], label=d[k], linestyle=style[k])
        line, = ax2.plot(t, r[k], c[k], label=d[k], linestyle=style[k])
    
#ax1_upr = 2.6
#ax1_lwr = 2
#ax2_upr = 1
#ax2_lwr = 0  

ax1.set_ylim(ax1_lwr-space,ax1_upr)
ax2.set_ylim(ax2_lwr, ax2_upr+space)    


#ax1.xaxis.set_major_locator(majorLocator)
#ax1.xaxis.set_minor_locator(minorLocator)
ax1.grid(True, 'both')
#ax2.xaxis.set_major_locator(majorLocator)
#ax2.yaxis.set_minor_locator(minorLocator)
ax2.grid(True, 'both')

#ytx = np.linspace(ax1_lwr, ax1_upr, ax1_upr-ax1_lwr+1)
ytx = np.linspace(ax1_lwr, ax1_upr, 2)
ax1.set_yticks(ytx)
#ax1.set_yticklabels(list(str(yl) for yl in ytx))

ytx = np.linspace(ax2_lwr, ax2_upr, 6)
ax2.set_yticks(ytx)

ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)  # don't put tick labels at the top
ax2.xaxis.tick_bottom()

d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass plot, just so we don't keep repeating them
grad = ratio[1]/ratio[0]
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-grad*d, +grad*d), **kwargs)        # top-left diagonal
ax1.plot((1 - d, 1 + d), (-grad*d, +grad*d), **kwargs)  # top-right diagonal

kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal





    
#ax = plt.gca()
##ax.set_xlim(0, 1)
#
#

#
#ax.yaxis.labelpad = 10
#    
handles, labels = ax1.get_legend_handles_labels()
labels, handles = zip(*sorted(zip(map(float,labels), handles)))
labels = map(formatLabel, labels)
ax2.legend(handles, labels, title='Damping factor', bbox_to_anchor=(0.96, 1.2))
#        


ax2.set_xlabel('time (s)')
ax2.set_ylabel('|z|', rotation='horizontal')
ax2.yaxis.set_label_coords(-0.11,(ax1_size+ax2_size)/2)

sp.plot(plt)

#plt.show()
#plt.savefig('/monochrome_figures/damping_broken_axis_1_sub.pdf', format='pdf')
#plt.savefig('said_and_done_damping.pdf', format='pdf', bbox_inches='tight')
#plt.savefig('{}.pdf'.format(savefile), format='pdf', bbox_inches='tight')
#print('Saved figure {}.pdf'.format(savefile))
#plt.close()




