#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 15:15:05 2019

@author: keziah
"""

import os.path
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from save_plot import SavePlot
import seaborn as sns
from check_onsets import CheckOnsets


def plot_audio(file, sp, manual_onsets=None, found_onsets=None):
    
    sns.set_style('whitegrid')

    audio, sr = sf.read(file)
    
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
        
#    print(len(audio))
        
    plot_ms = False
    
    t = np.linspace(0, len(audio)/sr, len(audio))
    
    if plot_ms:
        t *= 1000
    
    
    t0 = 0
    t1 = len(audio) # int(0.4*sr) #  
    
    plt.plot(t[t0:t1], audio[t0:t1], color='#e02323') # '#ad0d0d' '#cc1c1c'
             
#    if onset is not None:
##        plt.axvline(onset, color='lime')
#        plt.axvline(1000*onset, color='indigo', linestyle='--')
#        
#    if found is not None:
#        plt.axvline(1000*found, color='mediumorchid', linestyle='--')
    
    if manual_onsets is not None and found_onsets is not None:
             
        correct, diff = CheckOnsets.compare(manual_onsets, found_onsets, 50)
        
        if correct.size > 0:
            for n, idx in enumerate(correct):
                # correctly found onset
                onset = found_onsets[idx]
                # remove corresponding onset from manual_onsets
                man = manual_onsets + (diff[n]/1000)
                w = np.where(np.isclose(man, onset))[0]
                manual_onsets = np.delete(manual_onsets, w)
                # plot onset
                if plot_ms:
                    onset *= 1000
                plt.axvline(onset, color='lime')
            
            # remove correct onsets from found
            found_onsets = np.delete(found_onsets, correct)
                
        # plot false negatives
        for onset in manual_onsets:
            if plot_ms:
                onset *= 1000
            plt.axvline(onset, color='indigo', linestyle='--')
        # plot false positives
        for onset in found_onsets:
            if onset < t[t1-1]:
                if plot_ms:
                    onset *= 1000
                plt.axvline(onset, color='mediumorchid', linestyle='--')
                
#    ax = plt.gca()
#    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
                
    plt.grid(True)
    if plot_ms:
        xlabel = 'Time (ms)'
    else:
        xlabel = 'Time (s)'
    plt.xlabel(xlabel)
    plt.ylabel('Amplitude')
    
    sp.plot(plt)
    

if __name__ == '__main__':
    
    plt.style.use('thesis-small-fig')
    
    user = os.path.expanduser('~')
    audio_root_dir = os.path.join(user, 'Iowa', 'all')
    percussion_dir = os.path.join(audio_root_dir, 'Percussion')
    savepath = '/home/keziah/Documents/writing/thesis/figures/'
    
    params = {
            'bow':{'file':'Vibraphone.bow/Vibraphone.bow.A4.stereo.wav',
                     'savename':'vibraphone_bow_400ms.pdf',
                     'onset':[0.174],
                     'found':[0.022]},
#              'strike':
#                  {'file': 'Vibraphone.dampen/Vibraphone.dampen.ff.A4.stereo.wav',
#                   'savename':'vibraphone_strike.pdf',
#                   'onset':0.015,
#                   'found':0.019}
                  }
    
    for k, dct in params.items():
        file = os.path.join(percussion_dir, dct['file'])
        savefile = os.path.join(savepath, dct['savename'])
        sp = SavePlot(False, savefile, auto_overwrite=True)
        plot_audio(file, sp, manual_onsets=dct['onset'], 
                   found_onsets=dct['found'])
        
    
    
