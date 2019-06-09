#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 14:57:08 2016

@author: keziah
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
from save_plot import SavePlot
import seaborn as sns
import os.path


def formatLabel(label):
    if label == 27.5:
        return('{0:.1f} Hz'.format(label))
    else:
        return('{0:.3f} Hz'.format(label))
        
        
def getEllipseParams(x, y):
    """ Get the semimajor and semiminor axes, 'a' and 'b' respectively,
        of the ellipse defined by 'x' and 'y'
    """
    mx_x, mx_y = getMaxima(x,y)
    b, a = sorted([mx_x, mx_y])
    return a, b


def getMaxima(x, y):
    """ Get the semimajor and semiminor axes, 'a' and 'b' respectively,
        of the ellipse defined by 'x' and 'y'
    """
#    mx_x = (np.abs(np.min(x)) + np.max(x)) / 2
#    mx_y = (np.abs(np.min(y)) + np.max(y)) / 2
#    
    mx_x = np.max(x)
    mx_y = np.max(y)
    return mx_x, mx_y

        
def plot_complex(f0, i, nOsc, end):
    
    d = 0.0001
    
    sr = 48000
    
    dur = 5
    t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
    audio = np.sin(t)
    audio = np.append(audio, np.zeros(sr))
    gain = 5
    
    method = DetectorBank.runge_kutta #central_difference #
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_unnormalized
    d = 0.0001
    gain = 5
    f = np.array([f0])
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
        
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128) 
    det.getZ(z)
    
    r = np.zeros(z.shape)
    det.absZ(r, z)
    
    # number of oscillations to plot
#    nOsc = 20 #5
    # signal may have been modulated by DetectorBank
    # detFreq is the frequency the detector is actually operating at, therefore
    # the frequency of the orbits
    detFreq = det.getW(0)/(2*np.pi)
    # number of samples in nOsc
    sOsc = int(nOsc/detFreq * sr)
    
    if end == 'first':
        t0 = 0 #(dur*sr)-sOsc # int(0.0 * sr)
        t1 = sOsc # dur*sr # int(nOsc/f[0] * sr)
    elif end == 'last':
        t0 = (dur*sr)-sOsc # int(0.0 * sr)
        t1 = dur*sr # int(nOsc/f[0] * sr)
    
    x = z[0].real[t0:t1]
    y = z[0].imag[t0:t1]
    
#    re_idx = np.where(np.diff(np.sign(x)))[0]
#    im_idx = np.where(np.diff(np.sign(y)))[0]
#    
#    x_sq = x[im_idx]
#    y_sq = y[re_idx]
#    
#    means = [np.mean(np.abs(x_sq)), np.mean(np.abs(y_sq))]
#    b, a = sorted(means)
    
    
#    mx_x, mx_y = getMaxima(x,y)
#    
#    iScale = mx_x/mx_y
#    
#    yScaled = y * iScale
#    
    
#    
#    fig = plt.figure(i)
#    plt.plot(z[0][t0:t1])
#    plt.xlabel('Samples')
#    plt.ylabel('z', rotation='horizontal')
#    plt.grid()
#    plt.show()
#    plt.close()
    
    c = ['darkmagenta'] # ['black'] #  
    
    a, b = getEllipseParams(x, y)
    e = np.sqrt(a**2 - b**2) / a

    plt.plot(x, y, c[0])
    plt.grid(True)
    
#    plt.title('{}Hz'.format(f0))
    plt.xlabel('real')
    plt.ylabel('imag')
    
    fig = plt.gcf()
    fig.set_size_inches(8, 8)
#    fig.set_size_inches(6, 6)
    
    savefile = 'complex_response_{}Hz_{}{}.pdf'.format(f[0], end, nOsc)
    savepath = '.' # 'monochrome_figures' # 
    
    sp = SavePlot(False, os.path.join(savepath, savefile), auto_overwrite=True)
    
    sp.plot(plt)
    
#    plt.show()
#    savefile = 'complex_response_{}Hz_last{}.pdf'.format(f[0], nOsc)
#    plt.savefig(savefile, format='pdf', bbox_inches='tight')
#    print('Saved figure ', savefile)
#    plt.close()
            
    
    return e
    
if __name__ == '__main__':
    
    plt.style.use('thesis-square-fig')
#    plt.style.use('thesis-small-fig')
    sns.set_style('whitegrid')
    
    freq = [5, 400] #np.linspace(1, 4200, num=4200) #[400]#, 20, 400, 1600] 
    
    params = {'first':20, 'last':5}
    
#    out = 'Frequency,Eccentricity\n'
    
    i = 1
    
    
    for k in params.keys():
        for f0 in freq:
            e = plot_complex(f0, i, params[k], k)
            print('** {}Hz **'.format(f0))
            print('Eccentricity: {:g}'.format(e))
            i += 1
#        out += '{},{}\n'.format(f0, e)
#        print('{:.0f}%'.format(100*(f0/len(freq))), end='\r')
##            
#    with open('../Sandpit/results/eccentricity.csv', 'w') as fileobj:
#        fileobj.write(out)
#        
#    plt.show()
#    plt.close()
            
            
    
    