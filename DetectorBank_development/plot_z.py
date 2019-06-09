#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 13:58:54 2018

@author: keziah
"""


import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns
from save_plot import SavePlot
import os.path

plt.style.use('thesis-small-fig')

sr = 48000
linecolour = 'darkmagenta' # 'black' # 
#ticklabelsize = 14
#labelsize = 14# 20
figpath = '/home/keziah/onsets/hsj/Visualisation/'
#figpath = '/home/keziah/onsets/hsj/Visualisation/monochrome_figures/'

def formatLabel(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.3f} Hz'.format(label))
        
        
def getDetectorBank(f0, getAbs=False):
    
    print('** {}Hz **'.format(f0))
    
    dur = 2
    t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
    audio = np.sin(t)
    
#    audio = 2 * np.random.random(sr*dur) - 1
    
    audio = np.append(audio, np.zeros(sr))
    
    
    
    method = DetectorBank.runge_kutta #central_difference# 
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    d = 0.0001
    gain = 5
    f = np.array([f0])
#    f = np.array([22])
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128) 
    det.getZ(z)
    
    if getAbs:
        r = np.zeros(z.shape)
        det.absZ(r, z)
        return r
        
    else:
        return z
    
    
def plot_real(f0, sp=None):
    
    z = getDetectorBank(f0, getAbs=False)
    
    response = z[0].real
    
    t0 = 0
    t1 = len(response)
        
    plt.figure()
    plt.plot(response[t0:t1], marker=',', linestyle='')
    plt.xlabel('Samples')
    plt.ylabel('z', rotation='horizontal')
    plt.grid(True)
    
    if sp is not None:
        sp.plot(plt)
    
#    plt.show()
#    plt.close()
    
    
#    plt.show()
    #savefile = 'complex_response_{}Hz_1.pdf'.format(f[0])
    #plt.savefig(savefile, format='pdf', bbox_inches='tight')
    #print('Saved figure ', savefile)
#    plt.close()
    
    
def plot_absolute(f0, sp=None):
    
    r = getDetectorBank(f0, getAbs=True)
    
    response = r[0]
    
    t0 = 0
    t1 = sr #len(response)
    
    t = np.linspace(t0, t1/sr, t1-t0)
        
    plt.figure()
    plt.plot(t, response[t0:t1], color=linecolour)#, marker=',', linestyle='')
    plt.xlabel('Time (s)')#, fontsize=labelsize) #'Samples')
    plt.ylabel('|z|', rotation='horizontal')#, fontsize=labelsize)
    plt.grid(True)
    
    ax = plt.gca()
    ax.yaxis.labelpad = 10
    
    ax.tick_params('both')#, labelsize=ticklabelsize)
    
    if sp is not None:
        sp.plot(plt)
    
#    plt.show()
    #savefile = 'complex_response_{}Hz_1.pdf'.format(f[0])
    #plt.savefig(savefile, format='pdf', bbox_inches='tight')
    #print('Saved figure ', savefile)
    
    
def plot_complex(f0, sp=None):
    
    z = getDetectorBank(f0, getAbs=False)
    
    x = z[0].real
    y = z[0].imag
    
    t0 = 0
    t1 = int(0.2*sr) #len(x)
    
    plt.figure()
    plt.plot(x[t0:t1], y[t0:t1], color=linecolour)#, marker=',', linestyle='')
    plt.xlabel('Re(z)')#, fontsize=labelsize)
    plt.ylabel('Im(z)', rotation=0)#, fontsize=labelsize
    plt.grid(True)
    
    ax = plt.gca()
    tkx = np.linspace(-0.4, 0.4, num=5)
    ax.set_xticks(tkx)
    ax.set_yticks(tkx)
    
    ax.yaxis.set_label_coords(-0.14, 0.53)
    
    ax.tick_params('both')#, labelsize=ticklabelsize)
    
    if sp is not None:
        sp.plot(plt)
    
    
if __name__ == '__main__':
    
#    freq = [5, 20, 400, 1600]
#    
#    for f0 in freq:
#        plot_complex(f0)
#        print()
        
    f0 = 100 #400 #3169.28 #
#    plot_real(f0)
    
    sns.set_style('whitegrid')
    
    save = False
    
    figname = '{}Hz_line_label.pdf'.format(f0)
    sp = SavePlot(save, savefile=os.path.join(figpath, figname))
    plot_absolute(f0, sp=sp)
    
    figname = '{}Hz_spiral_label.pdf'.format(f0)
    sp = SavePlot(save, savefile=os.path.join(figpath, figname))
    plot_complex(f0, sp=sp)
    
#    plt.show()
#    plt.close()
    
