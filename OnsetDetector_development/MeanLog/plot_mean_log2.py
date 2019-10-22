#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the mean log, including shaded areas and onsets
"""

from detectorbank import DetectorBank, NoteDetector, OnsetDict
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import seaborn as sns
import os.path


def getParams():
    
    ds = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]
    bws = [0.922, 1.832, 2.752, 3.660, 4.86]
    thrs = [0.0003, 0.0003, 0.0003, 0.0003, 0.0001]
    
    method = DetectorBank.runge_kutta 
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    damping = 0.0001
    gain = 25
    edo = 12
    idx = ds.index(damping)
    bw = bws[idx]
    thr = thrs[idx]
    
    p = {'method':method, 'f_norm':f_norm, 'a_norm':a_norm, 'damping':damping,
         'gain':gain, 'edo':edo, 'real_bandwidth':bw, 'req_bandwidth':0,
         'threshold':thr}
    
    return p
    

def plotMean(audio, sr, freq, onset, found):
    
    sns.set_style('whitegrid')
    
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    
    offset = 1/4
    pad = np.zeros(int(sr*offset))
#    pad.fill(audio[0])
    
    audio = np.append(pad, audio)
    
    params = getParams()
    method = params['method']
    f_norm = params['f_norm']
    a_norm = params['a_norm']
    d = params['damping']
    gain = params['gain']
    
    bw = params['real_bandwidth']
    edo = params['edo']
    
    f = makeBand(freq, bw, edo)
    
    bandwidth = np.zeros(len(f))
    det_char = np.array(list(zip(f, bandwidth)))
    
    det = DetectorBank(sr, audio.astype(np.float32), 4, det_char, 
                       method|f_norm|a_norm, d, gain)
    
    z = np.zeros((len(f),len(audio)), dtype=np.complex128) 
    det.getZ(z)
    
    r = np.zeros(z.shape)
    det.absZ(r, z)
    
    meanlog = np.zeros(len(audio))
    
    for n in range(len(meanlog)):
        mean = 0
        for k in range(det.getChans()):
            mean += zeroLog(r[k,n])
        meanlog[n] = mean
    
        
    t = np.linspace(0, len(audio)/sr, len(audio))
    
    t0 = 0.25
    t1 = 0.5
    
    i0 = int(sr*t0)
    i1 = int(sr*t1)
    
    plt.figure()
    plt.plot(t[i0:i1], meanlog[i0:i1])
    
    plt.axvline(onset+offset, color='lime') # linestyle='--', )
    for t in found:
        plt.axvline(t+offset, linestyle='--', color='red')
        
    ax = plt.gca()
    xtx = ax.get_xticks()
    xtxlab = ['{:.0f}'.format(1000*(item-offset)) for item in xtx]
    ax.set_xticklabels(xtxlab)
    
#    plt.title('{:.3f}Hz'.format(freq))
    plt.xlabel('Time (ms)')
#    plt.ylabel('Log(|z|)')
    plt.ylabel('Mean log')
    plt.grid(True)
        
    plt.show()
    plt.close()    
    
def makeBand(f0, b=0.922, edo=12):
    """ Get array of frequencies in a critical band
    
        Parameters
        ----------
        f0 : float
            centre frequency
        b : float
            detector bandwidth (default is 1.16Hz)
        edo : int
            number of divisions in octave (default is 12)
            
        Returns
        -------
        array for critical band frequencies around f0
    """
    
    # denominator for half a semitone in given EDO
    # eg for 12EDO, f=f0*2**(1/24)
    half_semitone = 2*edo
    
    # make output array
    freq = np.zeros(0)
    
    # get frequencies from centre +/- half a semitone
    for i in (-1, 1):
        
        f = f0
        f1 = f0 * 2**(i/half_semitone)
        
        # difference between current and stop frequency
        diff = i*(f1-f) # keep diff positive

        # until diff is at minimum or f is within b/4 of stop value
        while i*(f1-f) <= diff and i*(f1-f) > b/4:
            diff = i*(f1-f)
            f += (i*b) # when i == -1, b will be subtracted
            freq = np.append(freq, f)
                        
    freq = np.append(freq, f0)
    
    freq.sort()
        
    return freq

    

def zeroLogArr(arr):
    
    result = np.zeros(len(arr))
    
    for i, value in enumerate(arr):
        if value != 0:
            result[i] = np.log(value)
            
    return result


def zeroLog(value):
    
    if value != 0:
        return np.log(value)
            
    else:
        return 0


def getOnsets(audio, sr, freq):
    
    params = getParams()
    method = params['method']
    f_norm = params['f_norm']
    a_norm = params['a_norm']
    d = params['damping']
    gain = params['gain']
    bw = params['req_bandwidth']
    edo = params['edo']
    threshold = params['threshold']
    
    path = 'log'
    if not os.path.exists(path):
        os.makedirs(path)
    
    nd = NoteDetector(sr, audio.astype(np.float32), freq, edo, 
                      bw, method|f_norm|a_norm, d, gain,
                      path)
    
    onsets = OnsetDict()
    
    nd.analyse(onsets, threshold)
    
    return onsets
    
    

if __name__ == '__main__':

    file = 'Trumpet.vib.ff.C4.stereo.wav'
    
    audio, sr = sf.read(file)
    
    onset = 0.076 # manually found onset time
    
    k = -9
    freq = np.array([440*2**(i/12) for i in [k]]) # [k-1, k, k+1]])
    
    onsets = getOnsets(audio, sr, freq)
    found = onsets[0] 
    found = sorted(list(found))
    found = np.array(found)
    found = found/sr
    
    print(found)
    
    plotMean(audio, sr, freq[0], onset, found)
    
    
