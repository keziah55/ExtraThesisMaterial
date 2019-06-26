#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if the DetectorBank is susceptible to false detections like residue pitch
and combintation tones.

Select which by setting the `mode` in if __name__ == '__main__'
"""

import numpy as np
from detectorbank import DetectorBank
import matplotlib.pyplot as plt
import seaborn as sns


def combination_tones(f, kmax=5, sr=48000):
    
    f1 = np.max(f)
    f2 = np.min(f)
    
    diff_tone = f1-f2
    
    f = np.append(f, diff_tone)
    
    for k in range(1, kmax):
        com_tone = f1 - k*(f2-f1)
        if 0 < com_tone < sr/2:
            f = np.append(f, com_tone)
        else:
            print('{} Hz out of range')
    
    return f


def residue_pitch(f0, size, sr=48000):
     f = np.array([f0*k for k in range(2, size) if f0*k < sr/2])
     return f
    
    
def make_audio(sr, f, duration=2):
    
    t = np.linspace(0, 2*np.pi*duration, sr*duration)
    audio = np.zeros(sr*duration)
    
    for freq in f:
        audio += np.sin(freq*t)
        
    audio /= np.max(audio)
    audio = np.append(audio, np.zeros(sr))
    
    return audio
    

def get_responses(sr, audio, f):
    
    method = DetectorBank.runge_kutta
    f_norm = DetectorBank.freq_unnormalized
    a_norm = DetectorBank.amp_normalized
    gain = 25
    d = 0.0001
    bandwidth = np.zeros(len(f))
    #bandwidth.fill(5)  # uncomment for degerate detectors
    det_char = np.array(list(zip(f, bandwidth)))
     
    z = np.zeros((len(f),len(audio)), dtype=np.complex128)    
    r = np.zeros(z.shape) 
    
    det = DetectorBank(sr, audio, 4, det_char, method|f_norm|a_norm, d, gain)
    
    det.getZ(z) 
    det.absZ(r, z)
    
    return r


def plot_repsonses(sr, f, r):
    
    t = np.linspace(0, r.shape[1]/sr, r.shape[1])
    
    labels = ['{} Hz'.format(f[k]) for k in range(len(f))]
    c = ['red', 'darkorange', 'deeppink', 'darkmagenta', 'green', 
         'skyblue', 'blue', 'darkslategrey']
    
    
    for k in range(r.shape[0]):
        plt.plot(t, r[k], color=c[k], label=labels[k])
        
    plt.xlabel('Time (s)')
    plt.ylabel('|z|', rotation='horizontal')
    plt.grid(True)
    #plt.legend()
    
    plt.show()
    plt.close()
    

if __name__ == '__main__':
    
    modes = ['residue', 'combination']
    mode = modes[0] # change to 1 for combination tones

    sr = 48000
        
    if mode == 'residue':
        f0 = 250
        # get audio frequencies
        f = residue_pitch(f0, size=9, sr=sr)
        # make tones at these freqs
        audio = make_audio(sr, f)
        # put f0 in freq array for DetectorBank to look for
        f = np.append(f0, f)
        
        
    elif mode == 'combination':
        # make tones at these freqs
        f = np.array([1000, 1500])
        audio = make_audio(sr, f)
        # make array of freqs for DetectorBank to look for
        f = combination_tones(f, kmax=6, sr=sr)

    # get DetectorBank responses
    r = get_responses(sr, audio, f)
    
    sns.set_style('whitegrid')
    plot_repsonses(sr, f, r)
    
    for n, freq in enumerate(f):
        print('{:4.0f} Hz response max: {:.6f}'.format(freq, np.max(r[n])))
    